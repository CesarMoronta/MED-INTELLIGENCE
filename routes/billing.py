import os
import requests
from flask import Blueprint, request, jsonify, session
from database import (get_connection, get_visit, create_invoice,
                      list_pending_bills, list_invoices, get_user_by_id,
                      save_patient_billing_info, get_invoice_by_id,
                      get_patient_billing_info, get_all_clinic_settings)
from utils import requires_login, requires_role, get_current_user
from functools import wraps

billing_bp = Blueprint("billing_bp", __name__)

DGII_API_URL = os.environ.get("DGII_API_URL", "https://ecf-platform-backend-50801509587.us-central1.run.app")
DGII_API_KEY = os.environ.get("DGII_API_KEY", "ecf_live_5ad0ef2626e32d8967e13f655cee0c45f54d8509b1ef793149b881cbb52f25fe")

def sanitize_dgii_url(url: str) -> str:
    return url

def requires_billing_permission(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return jsonify({"success": False, "error": "Autenticación requerida."}), 401
        user = session["user"]
        role = user.get("role")
        if role in ("admin", "secretaria"):
            return f(*args, **kwargs)
        if role == "doctor":
            settings = get_all_clinic_settings()
            if settings.get("allow_doctor_billing") == "true":
                return f(*args, **kwargs)
        return jsonify({"success": False, "error": "Permiso denegado."}), 403
    return wrapped

@billing_bp.route("/api/billing/pending", methods=["GET"])
@requires_login
@requires_billing_permission
def api_list_pending_bills():
    return jsonify({"success": True, "pending": list_pending_bills()})

@billing_bp.route("/api/billing/invoices", methods=["GET"])
@requires_login
@requires_billing_permission
def api_list_invoices():
    u = get_current_user()
    invoices = list_invoices()
    if u.get("role") == "secretaria":
        invoices = [i for i in invoices if i.get("invoice_type") == "consulta"]
    return jsonify({"success": True, "invoices": invoices})

@billing_bp.route("/api/billing/charge", methods=["POST"])
@requires_login
@requires_billing_permission
def api_charge_visit():
    data = request.json or {}
    visit_id = data.get("visit_id")
    payment_method = data.get("payment_method", "efectivo").lower()
    tipo_ecf = data.get("tipo_ecf", "32")
    # Crédito
    is_credit = data.get("is_credit", False)
    amount_paid_input = data.get("amount_paid")
    due_date_input = data.get("due_date") or None

    if not visit_id:
        return jsonify({"success": False, "error": "ID de visita es requerido."}), 400

    visit = get_visit(visit_id)
    if not visit:
        return jsonify({"success": False, "error": "Visita no encontrada."}), 404

    # Verificar si ya existe una factura activa (no anulada totalmente) para esta visita
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(total), 0) FROM dbo.invoices WHERE visit_id = ?", visit_id)
    total_invoiced = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    if total_invoiced > 0:
        return jsonify({"success": False, "error": "Esta visita ya ha sido cobrada/facturada anteriormente."}), 400

    # Determinar código de pago
    # 1: Efectivo, 2: Tarjeta de Crédito/Débito
    forma_pago_code = 2 if payment_method == "tarjeta" else 1

    # Construir comprador
    comprador = {}
    if tipo_ecf == "31":
        rnc_comprador = data.get("rnc_comprador", "").strip()
        razon_social_comprador = data.get("razon_social_comprador", "").strip()
        correo_comprador = data.get("correo_comprador", "").strip() or None

        if not rnc_comprador or not razon_social_comprador:
            return jsonify({"success": False, "error": "RNC y Razón Social son requeridos para Crédito Fiscal (E31)."}), 400

        # Guardar en base de datos para el paciente de forma persistente
        save_patient_billing_info(visit.get("patient_id"), rnc_comprador, razon_social_comprador, correo_comprador)

        comprador["RNCComprador"] = rnc_comprador
        comprador["RazonSocialComprador"] = razon_social_comprador
    else:
        # Default E32 Consumidor Final
        comprador["RNCComprador"] = str(visit.get("patient_cedula") or "").replace("-", "").strip()
        comprador["RazonSocialComprador"] = visit.get("patient_name", "Consumidor Final")

    # Estructurar totales e ítem según comprobante (Cálculo de base e ITBIS)
    if tipo_ecf == "31":
        # Crédito Fiscal con 18% ITBIS incluido en los 3000.00
        monto_total = "3000.00"
        total_itbis = "457.63"
        monto_gravado = "2542.37"
        monto_exento = "0.00"
        indicador_facturacion = "1" # Gravado al 18%
        
        totales = {
            "MontoGravadoTotal": monto_gravado,
            "MontoGravadoI1": monto_gravado,
            "MontoExento": monto_exento,
            "ITBIS1": "18",
            "TotalITBIS": total_itbis,
            "TotalITBIS1": total_itbis,
            "MontoTotal": monto_total,
            "MontoNoFacturable": "0.00"
        }
        item_precio_unitario = monto_gravado
        item_monto = monto_gravado
    else:
        # Consumidor Final (E32) Exento
        monto_total = "3000.00"
        total_itbis = "0.00"
        monto_gravado = "0.00"
        monto_exento = "3000.00"
        indicador_facturacion = "4" # Exento
        
        totales = {
            "MontoGravadoTotal": monto_gravado,
            "MontoExento": monto_exento,
            "TotalITBIS": total_itbis,
            "MontoTotal": monto_total
        }
        item_precio_unitario = "3000.00"
        item_monto = "3000.00"

    # Construir el JSON del e-CF
    payload = {
        "ECF": {
            "Encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": tipo_ecf,
                    "IndicadorEnvioDiferido": "1",
                    "IndicadorMontoGravado": "0",
                    "IndicadorServicioTodoIncluido": "1" if tipo_ecf == "31" else "0",
                    "TipoIngresos": "01",
                    "TipoPago": "1",
                    "TablaFormasPago": {
                        "FormaDePago": [
                            {
                                "FormaPago": forma_pago_code,
                                "MontoPago": monto_total
                            }
                        ]
                    }
                },
                "Comprador": comprador,
                "Totales": totales
            },
            "DetallesItems": {
                "Item": {
                    "NumeroLinea": "1",
                    "IndicadorFacturacion": indicador_facturacion,
                    "NombreItem": "Consulta Medica General",
                    "IndicadorBienoServicio": "2", # 2: Servicio
                    "CantidadItem": "1",
                    "UnidadMedida": "43",
                    "PrecioUnitarioItem": item_precio_unitario,
                    "MontoItem": item_monto
                }
            }
        }
    }

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": DGII_API_KEY
    }

    try:
        res = requests.post(f"{DGII_API_URL}/api/v1/ecf/send", json=payload, headers=headers, timeout=15)
        res_data = res.json()
        
        if not res.ok or not res_data.get("enviado"):
            err_msg = res_data.get("errorMessage") or "Error al procesar la factura con la DGII."
            return jsonify({"success": False, "error": err_msg}), 502

        # Calcular montos de crédito
        total_amount = 3000.00
        if is_credit:
            try:
                paid = float(amount_paid_input) if amount_paid_input is not None else 0.0
            except (TypeError, ValueError):
                paid = 0.0
            paid = max(0.0, min(paid, total_amount))
            balance = round(total_amount - paid, 2)
        else:
            paid = total_amount
            balance = 0.0

        # Guardar en base de datos
        invoice_id = create_invoice(
            visit_id=visit_id,
            user_id=None,
            invoice_type="consulta",
            amount=float(monto_gravado) if tipo_ecf == "31" else 3000.00,
            itbis=float(total_itbis),
            total=total_amount,
            payment_method=payment_method,
            ecf_id=res_data.get("id"),
            encf=res_data.get("encf"),
            estado=res_data.get("estado", "Aceptado"),
            track_id=res_data.get("trackId"),
            codigo_seguridad=res_data.get("codigoSeguridad"),
            dgii_url=sanitize_dgii_url(res_data.get("dgiiUrl")),
            xml_url=res_data.get("xmlUrl"),
            tipo_ecf=f"E{tipo_ecf}",
            amount_paid=paid,
            balance_due=balance,
            due_date=due_date_input
        )

        if not invoice_id:
            return jsonify({"success": False, "error": "Error interno al guardar la factura."}), 500

        return jsonify({
            "success": True,
            "message": "Cobro registrado e e-CF generado con éxito.",
            "invoice_id": invoice_id,
            "invoice": {
                "encf": res_data.get("encf"),
                "estado": res_data.get("estado"),
                "codigo_seguridad": res_data.get("codigoSeguridad"),
                "dgii_url": sanitize_dgii_url(res_data.get("dgiiUrl")),
                "amount_paid": paid,
                "balance_due": balance,
                "due_date": due_date_input
            }
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": f"Error de conexión con la API de la DGII: {str(e)}"}), 502


def generate_subscription_invoice(user_id: int):
    """Genera factura de consumo (e-CF 32) automáticamente al suscribirse un doctor (RD$ 1,180.00)."""
    user = get_user_by_id(user_id)
    if not user:
        return False

    # Detalle: RD$ 1,000 + 18% ITBIS (RD$ 180) = RD$ 1,180.00
    payload = {
        "ECF": {
            "Encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "32",
                    "IndicadorEnvioDiferido": "1",
                    "IndicadorMontoGravado": "0",
                    "IndicadorServicioTodoIncluido": "0",
                    "TipoIngresos": "01",
                    "TipoPago": "1",
                    "TablaFormasPago": {
                        "FormaDePago": [
                            {
                                "FormaPago": 2, # 2: Tarjeta (simulado por PayPal)
                                "MontoPago": "1180.00"
                            }
                        ]
                    }
                },
                "Comprador": {
                    "RNCComprador": str(user.get("matricula") or "").replace("-", "").strip() or "00000000000",
                    "RazonSocialComprador": user.get("full_name") or user.get("username")
                },
                "Totales": {
                    "MontoGravadoTotal": "1000.00",
                    "MontoGravadoI1": "1000.00",
                    "ITBIS1": "18",
                    "TotalITBIS": "180.00",
                    "TotalITBIS1": "180.00",
                    "MontoTotal": "1180.00"
                }
            },
            "DetallesItems": {
                "Item": {
                    "NumeroLinea": "1",
                    "IndicadorFacturacion": "1", # 1: Gravado al 18%
                    "NombreItem": "Suscripcion Mensual MED-INTELLIGENCE VIP",
                    "IndicadorBienoServicio": "2",
                    "CantidadItem": "1",
                    "UnidadMedida": "43",
                    "PrecioUnitarioItem": "1000.00",
                    "MontoItem": "1000.00"
                }
            }
        }
    }

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": DGII_API_KEY
    }

    try:
        res = requests.post(f"{DGII_API_URL}/api/v1/ecf/send", json=payload, headers=headers, timeout=15)
        res_data = res.json()
        
        if res.ok and res_data.get("enviado"):
            create_invoice(
                visit_id=None,
                user_id=user_id,
                invoice_type="suscripcion",
                amount=1000.00,
                itbis=180.00,
                total=1180.00,
                payment_method="tarjeta",
                ecf_id=res_data.get("id"),
                encf=res_data.get("encf"),
                estado=res_data.get("estado", "Aceptado"),
                track_id=res_data.get("trackId"),
                codigo_seguridad=res_data.get("codigoSeguridad"),
                dgii_url=sanitize_dgii_url(res_data.get("dgiiUrl")),
                xml_url=res_data.get("xmlUrl")
            )
            return True
    except Exception as e:
        print(f"Error emitiendo factura de suscripción: {e}")
    return False


@billing_bp.route("/api/billing/credit-note", methods=["POST"])
@requires_login
@requires_billing_permission
def api_create_credit_note():
    data = request.json or {}
    invoice_id = data.get("invoice_id")
    codigo_modificacion = data.get("codigo_modificacion", "1") # "1": Anulación, "3": Ajuste/Descuento
    monto_credito = data.get("monto_credito")
    concepto = data.get("concepto", "Nota de Credito").strip()

    if not invoice_id:
        return jsonify({"success": False, "error": "ID de factura es requerido."}), 400

    orig_invoice = get_invoice_by_id(invoice_id)
    if not orig_invoice:
        return jsonify({"success": False, "error": "Factura original no encontrada."}), 404

    # Verificar si es E31 o E32 (o consulta E32 histórica)
    tipo_orig = (orig_invoice.get("tipo_ecf") or "").strip()
    if not tipo_orig and orig_invoice.get("invoice_type") == "consulta":
        tipo_orig = "E32"

    if not (tipo_orig.endswith("31") or tipo_orig.endswith("32")):
        return jsonify({"success": False, "error": "Solo se pueden aplicar Notas de Crédito a comprobantes E31 y E32."}), 400

    # Determinar monto crédito
    try:
        monto_total = float(monto_credito) if monto_credito is not None else float(orig_invoice["total"])
    except ValueError:
        return jsonify({"success": False, "error": "Monto de crédito inválido."}), 400

    if monto_total <= 0:
        return jsonify({"success": False, "error": "El monto debe ser mayor a 0."}), 400
    if monto_total > float(orig_invoice["total"]):
        return jsonify({"success": False, "error": "El monto de la nota de crédito no puede exceder el total de la factura original."}), 400

    # Comprador
    if tipo_orig.endswith("31") and orig_invoice.get("patient_id"):
        billing_info = get_patient_billing_info(orig_invoice["patient_id"])
        if billing_info:
            comprador = {
                "RNCComprador": billing_info["rnc"],
                "RazonSocialComprador": billing_info["razon_social"]
            }
        else:
            comprador = {
                "RNCComprador": str(orig_invoice.get("patient_cedula") or "").replace("-", "").strip() or "00000000000",
                "RazonSocialComprador": orig_invoice.get("patient_name") or "Consumidor Final"
            }
    else:
        comprador = {
            "RNCComprador": str(orig_invoice.get("patient_cedula") or "").replace("-", "").strip() or "00000000000",
            "RazonSocialComprador": orig_invoice.get("patient_name") or "Consumidor Final"
        }

    # Cálculos
    if tipo_orig.endswith("31"):
        total_itbis = round(monto_total * 18 / 118, 2)
        monto_gravado = round(monto_total - total_itbis, 2)
        monto_exento = 0.00
        indicador_facturacion = "1" # Gravado al 18%
        
        totales = {
            "MontoGravadoTotal": f"{monto_gravado:.2f}",
            "MontoGravadoI1": f"{monto_gravado:.2f}",
            "MontoExento": f"{monto_exento:.2f}",
            "ITBIS1": "18",
            "TotalITBIS": f"{total_itbis:.2f}",
            "TotalITBIS1": f"{total_itbis:.2f}",
            "MontoTotal": f"{monto_total:.2f}",
            "MontoNoFacturable": "0.00"
        }
        item_precio_unitario = f"{monto_gravado:.2f}"
        item_monto = f"{monto_gravado:.2f}"
    else:
        # Exento (E32)
        monto_gravado = 0.00
        total_itbis = 0.00
        monto_exento = monto_total
        indicador_facturacion = "4" # Exento
        
        totales = {
            "MontoGravadoTotal": "0.00",
            "MontoExento": f"{monto_exento:.2f}",
            "TotalITBIS": "0.00",
            "MontoTotal": f"{monto_total:.2f}"
        }
        item_precio_unitario = f"{monto_total:.2f}"
        item_monto = f"{monto_total:.2f}"

    # Formatear la fecha original
    # created_at is returned as ISO string by get_invoice_by_id, e.g. "2026-06-23T11:08:48" or "2026-06-23"
    from datetime import datetime
    try:
        orig_created_at = orig_invoice.get("created_at")
        if "T" in orig_created_at:
            dt = datetime.fromisoformat(orig_created_at)
        else:
            dt = datetime.strptime(orig_created_at, "%Y-%m-%d")
        fecha_modificado = dt.strftime("%d-%m-%Y")
    except Exception:
        fecha_modificado = datetime.now().strftime("%d-%m-%Y")

    payload = {
        "ECF": {
            "Encabezado": {
                "Version": "1.0",
                "IdDoc": {
                    "TipoeCF": "34",
                    "IndicadorNotaCredito": "0",
                    "IndicadorMontoGravado": "0",
                    "TipoIngresos": "01",
                    "TipoPago": "1"
                },
                "Comprador": comprador,
                "Totales": totales
            },
            "DetallesItems": {
                "Item": {
                    "NumeroLinea": "1",
                    "IndicadorFacturacion": indicador_facturacion,
                    "NombreItem": concepto,
                    "IndicadorBienoServicio": "2", # Servicio
                    "CantidadItem": "1",
                    "UnidadMedida": "43",
                    "PrecioUnitarioItem": item_precio_unitario,
                    "MontoItem": item_monto
                }
            },
            "InformacionReferencia": {
                "NCFModificado": orig_invoice["encf"],
                "FechaNCFModificado": fecha_modificado,
                "CodigoModificacion": str(codigo_modificacion)
            }
        }
    }

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": DGII_API_KEY
    }

    try:
        res = requests.post(f"{DGII_API_URL}/api/v1/ecf/send", json=payload, headers=headers, timeout=15)
        res_data = res.json()
        
        if not res.ok or not res_data.get("enviado"):
            err_msg = res_data.get("errorMessage") or "Error al procesar la Nota de Crédito con la DGII."
            return jsonify({"success": False, "error": err_msg}), 502

        # Guardar en base de datos con signo negativo
        success = create_invoice(
            visit_id=orig_invoice.get("visit_id"),
            user_id=None,
            invoice_type="nota_credito",
            amount=-monto_gravado if tipo_orig.endswith("31") else -monto_total,
            itbis=-total_itbis,
            total=-monto_total,
            payment_method=orig_invoice.get("payment_method", "efectivo"),
            ecf_id=res_data.get("id"),
            encf=res_data.get("encf"),
            estado=res_data.get("estado", "Aceptado"),
            track_id=res_data.get("trackId"),
            codigo_seguridad=res_data.get("codigoSeguridad"),
            dgii_url=sanitize_dgii_url(res_data.get("dgiiUrl")),
            xml_url=res_data.get("xmlUrl"),
            tipo_ecf="E34"
        )

        if not success:
            return jsonify({"success": False, "error": "Error interno al guardar la Nota de Crédito."}), 500

        return jsonify({
            "success": True,
            "message": "Nota de Crédito registrada y e-CF generado con éxito.",
            "invoice": {
                "encf": res_data.get("encf"),
                "estado": res_data.get("estado"),
                "codigo_seguridad": res_data.get("codigoSeguridad"),
                "dgii_url": sanitize_dgii_url(res_data.get("dgiiUrl"))
            }
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": f"Error de conexión con la API de la DGII: {str(e)}"}), 502
