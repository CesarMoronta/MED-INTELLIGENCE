import os
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import (list_patients, add_patient, get_patient, update_patient,
                      delete_patient, log_audit_action, get_patient_vitals_history,
                      get_active_medications, get_patient_red_alerts, get_patient_billing_info,
                      mark_patient_deceased, get_patient_account_statement)
from utils import requires_login, requires_role, get_current_user, get_client_ip, format_cedula
from werkzeug.utils import secure_filename

patients_bp = Blueprint("patients_bp", __name__)


@patients_bp.route("/api/patients", methods=["GET"])
@requires_login
def api_get_patients():
    search = (request.args.get("search") or "").strip()
    u = get_current_user()
    # Doctor solo ve sus propios pacientes (los que tienen citas o visitas con él)
    doctor_id = u.get("id") if u.get("role") == "doctor" else None
    patients = list_patients(search or None, doctor_id=doctor_id)
    return jsonify({"success": True, "patients": patients})


@patients_bp.route("/api/patients", methods=["POST"])
@requires_login
@requires_role("admin", "secretaria")  # Doctor NO puede crear pacientes
def api_save_patient():
    import re
    data         = request.json or {}
    raw_cedula   = (data.get("cedula") or "").strip()
    cedula_digits = re.sub(r"\D", "", raw_cedula)
    if len(cedula_digits) != 11:
        return jsonify({"success": False, "error": "La cédula debe contener exactamente 11 dígitos numéricos."}), 400
    cedula       = format_cedula(cedula_digits)
    name         = (data.get("name") or "").strip().upper()
    dob          = data.get("dob") or "1990-01-01"
    gender       = data.get("gender") or "Otro"
    antecedentes = data.get("antecedentes") or {}
    phone        = (data.get("phone") or "").strip() or None
    blood_type   = (data.get("blood_type") or "").strip() or None
    photo_url    = (data.get("photo_url") or "").strip() or None

    if not cedula:
        return jsonify({"success": False, "error": "La cédula del paciente es obligatoria."}), 400
    if not name:
        return jsonify({"success": False, "error": "El nombre completo del paciente es requerido."}), 400

    if dob:
        try:
            dob_dt = datetime.strptime(dob, "%Y-%m-%d").date()
            if dob_dt > datetime.now().date():
                return jsonify({"success": False, "error": "La fecha de nacimiento no puede estar en el futuro."}), 400
        except ValueError:
            return jsonify({"success": False, "error": "La fecha de nacimiento no es válida. Debe estar en formato AAAA-MM-DD (ej. 1990-05-15)."}), 400

    u = get_current_user()
    registered_by = u.get("id")

    patient_id = add_patient(cedula, name, dob, gender, antecedentes, phone, blood_type, registered_by, photo_url)
    if patient_id:
        log_audit_action(
            username=u.get("username"), action="CREATE", entity="Patient",
            details=f"Registrado paciente '{name}' cédula '{cedula}'",
            ip_address=get_client_ip(), user_id=u.get("id")
        )
        return jsonify({"success": True, "patient": {
            "id": patient_id, "cedula": cedula, "name": name, "dob": dob, "gender": gender
        }})
    return jsonify({"success": False, "error": "Cédula ya registrada o error al guardar."}), 409


@patients_bp.route("/api/patients/<int:patient_id>", methods=["GET"])
@requires_login
def api_get_patient(patient_id):
    patient = get_patient(patient_id)
    if patient is None:
        return jsonify({"success": False, "error": "Paciente no encontrado."}), 404
    return jsonify({"success": True, "patient": patient})


@patients_bp.route("/api/patients/<int:patient_id>", methods=["PUT"])
@requires_login
@requires_role("admin", "secretaria")
def api_update_patient(patient_id):
    import re
    data       = request.json or {}
    raw_cedula = (data.get("cedula") or "").strip()
    if raw_cedula:
        cedula_digits = re.sub(r"\D", "", raw_cedula)
        if len(cedula_digits) != 11:
            return jsonify({"success": False, "error": "La cédula debe contener exactamente 11 dígitos numéricos."}), 400
        cedula = format_cedula(cedula_digits)
    else:
        cedula = None
    name       = (data.get("name") or "").strip().upper() or None
    dob        = data.get("dob") or None
    if dob:
        try:
            dob_dt = datetime.strptime(dob, "%Y-%m-%d").date()
            if dob_dt > datetime.now().date():
                return jsonify({"success": False, "error": "La fecha de nacimiento no puede estar en el futuro."}), 400
        except ValueError:
            return jsonify({"success": False, "error": "La fecha de nacimiento no es válida. Debe estar en formato AAAA-MM-DD (ej. 1990-05-15)."}), 400
    gender     = (data.get("gender") or "").strip() or None
    phone      = (data.get("phone") or "").strip() or None
    blood_type = (data.get("blood_type") or "").strip() or None
    photo_url  = (data.get("photo_url") or "").strip() or None
    antecedentes = data.get("antecedentes")

    if not update_patient(patient_id, cedula, name, dob, gender, phone, blood_type, antecedentes, photo_url):
        return jsonify({"success": False, "error": "No se pudo actualizar el paciente."}), 404

    u = get_current_user()
    log_audit_action(
        username=u.get("username"), action="UPDATE", entity="Patient",
        entity_id=str(patient_id),
        details=f"Actualización de datos del paciente ID={patient_id}",
        ip_address=get_client_ip(), user_id=u.get("id")
    )
    return jsonify({"success": True, "patient": get_patient(patient_id)})


@patients_bp.route("/api/patients/<int:patient_id>", methods=["DELETE"])
@requires_login
@requires_role("admin")
def api_delete_patient(patient_id):
    if delete_patient(patient_id):
        u = get_current_user()
        log_audit_action(
            username=u.get("username"), action="DELETE", entity="Patient",
            entity_id=str(patient_id), ip_address=get_client_ip(), user_id=u.get("id")
        )
        return jsonify({"success": True, "message": "Paciente eliminado correctamente."})
    return jsonify({"success": False, "error": "Paciente no encontrado."}), 404


# ─── Endpoints enriquecidos ───────────────────────────────────────────────────

@patients_bp.route("/api/patients/<int:patient_id>/vitals-history", methods=["GET"])
@requires_login
def api_patient_vitals_history(patient_id):
    """Retorna el historial de constantes vitales del paciente (últimas N visitas)."""
    limit = request.args.get("limit", 10, type=int)
    history = get_patient_vitals_history(patient_id, limit=limit)
    return jsonify({"success": True, "vitals_history": history})


@patients_bp.route("/api/patients/<int:patient_id>/active-medications", methods=["GET"])
@requires_login
def api_patient_active_medications(patient_id):
    """Retorna los medicamentos activos del paciente (recetas vigentes)."""
    meds = get_active_medications(patient_id)
    return jsonify({"success": True, "medications": meds})


@patients_bp.route("/api/patients/<int:patient_id>/alerts", methods=["GET"])
@requires_login
def api_patient_alerts(patient_id):
    """Retorna los diagnósticos en alerta Roja anteriores del paciente."""
    alerts = get_patient_red_alerts(patient_id)
    return jsonify({"success": True, "alerts": alerts})


@patients_bp.route("/api/patients/consulta-cedula/<cedula>", methods=["GET"])
@requires_login
def api_consultar_cedula(cedula):
    cedula_clean = cedula.replace("-", "").strip()
    if len(cedula_clean) != 11 or not cedula_clean.isdigit():
        return jsonify({"success": False, "error": "La cédula debe tener exactamente 11 dígitos."}), 400

    import os
    BASE_URL = os.environ.get("DGII_JCE_BASE_URL", "https://ecf-platform-backend-50801509587.us-central1.run.app")
    API_KEY  = os.environ.get("DGII_JCE_API_KEY", "ecf_live_5ad0ef2626e32d8967e13f655cee0c45f54d8509b1ef793149b881cbb52f25fe")

    url = f"{BASE_URL}/api/v1/dgii/jce?cedula={cedula_clean}"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }

    try:
        res = requests.get(url, headers=headers)
        data = res.json()

        if not res.ok or not data.get("found"):
            return jsonify({"success": False, "error": data.get("message", "Cédula no encontrada.")}), 404

        import base64
        foto_url = data.get("foto")
        if foto_url and foto_url.startswith("http"):
            try:
                foto_res = requests.get(foto_url, timeout=5)
                if foto_res.ok:
                    b64 = base64.b64encode(foto_res.content).decode("utf-8")
                    content_type = foto_res.headers.get("Content-Type", "image/jpeg")
                    data["foto"] = f"data:{content_type};base64,{b64}"
                else:
                    data["foto"] = None
            except Exception as ex:
                data["foto"] = None

        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Error de conexión: {str(e)}"}), 500


@patients_bp.route("/api/patients/consulta-rnc/<rnc>", methods=["GET"])
@requires_login
def api_consultar_rnc(rnc):
    rnc_clean = rnc.replace("-", "").strip()
    if len(rnc_clean) not in [9, 11] or not rnc_clean.isdigit():
        return jsonify({"success": False, "error": "El RNC/Cédula debe tener 9 u 11 dígitos."}), 400

    import os
    BASE_URL = os.environ.get("DGII_JCE_BASE_URL", "https://ecf-platform-backend-50801509587.us-central1.run.app")
    API_KEY  = os.environ.get("DGII_JCE_API_KEY", "ecf_live_5ad0ef2626e32d8967e13f655cee0c45f54d8509b1ef793149b881cbb52f25fe")

    url = f"{BASE_URL}/api/v1/dgii/rnc?value={rnc_clean}"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }

    try:
        res = requests.get(url, headers=headers)
        data = res.json()

        if not res.ok or not data.get("success"):
            return jsonify({"success": False, "error": data.get("message", "RNC no encontrado en la DGII.")}), 404

        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Error de conexión: {str(e)}"}), 500


@patients_bp.route("/api/patients/<int:patient_id>/billing-info", methods=["GET"])
@requires_login
def api_get_patient_billing_info(patient_id):
    info = get_patient_billing_info(patient_id)
    return jsonify({"success": True, "billing_info": info})


@patients_bp.route("/api/patients/<int:patient_id>/mark-deceased", methods=["POST"])
@requires_login
@requires_role("doctor")
def api_mark_patient_deceased(patient_id):
    """Marca un paciente como fallecido. Solo doctores. Requiere acta de defunción."""
    u = get_current_user()

    # Verificar que el paciente existe y está vivo
    patient = get_patient(patient_id)
    if not patient:
        return jsonify({"success": False, "error": "Paciente no encontrado."}), 404
    if patient.get("vital_status") == "Fallecido":
        return jsonify({"success": False, "error": "El paciente ya está registrado como fallecido."}), 409

    death_date = request.form.get("death_date")
    notes = request.form.get("notes", "").strip() or None

    if not death_date:
        return jsonify({"success": False, "error": "La fecha de fallecimiento es obligatoria."}), 400

    # Procesar el acta de defunción (archivo adjunto)
    cert_path = None
    if "certificate" in request.files:
        file = request.files["certificate"]
        if file and file.filename:
            upload_folder = os.environ.get("UPLOAD_FOLDER", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            filename = secure_filename(f"death_cert_{patient_id}_{file.filename}")
            save_path = os.path.join(upload_folder, filename)
            file.save(save_path)
            cert_path = f"/uploads/{filename}"

    ok = mark_patient_deceased(
        patient_id=patient_id,
        death_date=death_date,
        cert_path=cert_path,
        notes=notes,
        doctor_id=u.get("id"),
        doctor_username=u.get("username")
    )
    if ok:
        return jsonify({"success": True, "message": f"Paciente '{patient['name']}' marcado como fallecido."})
    return jsonify({"success": False, "error": "No se pudo registrar el fallecimiento."}), 500


@patients_bp.route("/api/patients/<int:patient_id>/account-statement", methods=["GET"])
@requires_login
@requires_role("doctor")
def api_patient_account_statement(patient_id):
    """Estado de cuenta del paciente. Solo visible para el doctor que lo haya atendido."""
    u = get_current_user()
    result = get_patient_account_statement(patient_id, doctor_id=u.get("id"))
    if result is None:
        return jsonify({"success": False, "error": "Acceso denegado o sin registros para este paciente."}), 403
    return jsonify({"success": True, "statement": result})
