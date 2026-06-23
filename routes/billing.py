import os
import requests
from flask import Blueprint, request, jsonify
from database import (get_connection, get_visit, create_invoice,
                      list_pending_bills, list_invoices, get_user_by_id)
from utils import requires_login, requires_role, get_current_user

billing_bp = Blueprint("billing_bp", __name__)

DGII_API_URL = os.environ.get("DGII_API_URL", "https://ecf-platform-backend-50801509587.us-central1.run.app")
DGII_API_KEY = os.environ.get("DGII_API_KEY", "ecf_live_5ad0ef2626e32d8967e13f655cee0c45f54d8509b1ef793149b881cbb52f25fe")

@billing_bp.route("/api/billing/pending", methods=["GET"])
@requires_login
@requires_role("admin", "secretaria")
def api_list_pending_bills():
    return jsonify({"success": True, "pending": list_pending_bills()})

@billing_bp.route("/api/billing/invoices", methods=["GET"])
@requires_login
@requires_role("admin", "secretaria")
def api_list_invoices():
    u = get_current_user()
    invoices = list_invoices()
    if u.get("role") == "secretaria":
        invoices = [i for i in invoices if i.get("invoice_type") == "consulta"]
    return jsonify({"success": True, "invoices": invoices})

@billing_bp.route("/api/billing/charge", methods=["POST"])
@requires_login
@requires_role("admin", "secretaria")
def api_charge_visit():
    data = request.json or {}
    visit_id = data.get("visit_id")
    payment_method = data.get("payment_method", "efectivo").lower()

    if not visit_id:
        return jsonify({"success": False, "error": "ID de visita es requerido."}), 400

    visit = get_visit(visit_id)
    if not visit:
        return jsonify({"success": False, "error": "Visita no encontrada."}), 404

    # Verificar si ya existe una factura para esta visita
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM dbo.invoices WHERE visit_id = ?", visit_id)
    existing_invoice = cursor.fetchone()
    cursor.close()
    conn.close()

    if existing_invoice:
        return jsonify({"success": False, "error": "Esta visita ya ha sido cobrada/facturada anteriormente."}), 400

    # Determinar código de pago
    # 1: Efectivo, 2: Tarjeta de Crédito/Débito
    forma_pago_code = 2 if payment_method == "tarjeta" else 1

    # Construir el JSON del e-CF 32 (Factura de Consumo) exenta de ITBIS por ser consulta médica
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
                                "FormaPago": forma_pago_code,
                                "MontoPago": "3000.00"
                            }
                        ]
                    }
                },
                "Comprador": {
                    "RNCComprador": str(visit.get("patient_cedula") or "").replace("-", "").strip(),
                    "RazonSocialComprador": visit.get("patient_name", "Consumidor Final")
                },
                "Totales": {
                    "MontoGravadoTotal": "0.00",
                    "MontoExento": "3000.00",
                    "TotalITBIS": "0.00",
                    "MontoTotal": "3000.00"
                }
            },
            "DetallesItems": {
                "Item": {
                    "NumeroLinea": "1",
                    "IndicadorFacturacion": "4", # 4: Exento de ITBIS
                    "NombreItem": "Consulta Medica General",
                    "IndicadorBienoServicio": "2", # 2: Servicio
                    "CantidadItem": "1",
                    "UnidadMedida": "43",
                    "PrecioUnitarioItem": "3000.00",
                    "MontoItem": "3000.00"
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

        # Guardar en base de datos
        success = create_invoice(
            visit_id=visit_id,
            user_id=None,
            invoice_type="consulta",
            amount=3000.00,
            itbis=0.00,
            total=3000.00,
            payment_method=payment_method,
            ecf_id=res_data.get("id"),
            encf=res_data.get("encf"),
            estado=res_data.get("estado", "Aceptado"),
            track_id=res_data.get("trackId"),
            codigo_seguridad=res_data.get("codigoSeguridad"),
            dgii_url=res_data.get("dgiiUrl"),
            xml_url=res_data.get("xmlUrl")
        )

        if not success:
            return jsonify({"success": False, "error": "Error interno al guardar la factura."}), 500

        return jsonify({
            "success": True,
            "message": "Cobro registrado e e-CF generado con éxito.",
            "invoice": {
                "encf": res_data.get("encf"),
                "estado": res_data.get("estado"),
                "codigo_seguridad": res_data.get("codigoSeguridad"),
                "dgii_url": res_data.get("dgiiUrl")
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
                dgii_url=res_data.get("dgiiUrl"),
                xml_url=res_data.get("xmlUrl")
            )
            return True
    except Exception as e:
        print(f"Error emitiendo factura de suscripción: {e}")
    return False
