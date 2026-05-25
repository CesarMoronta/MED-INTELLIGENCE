from flask import Blueprint, request, jsonify
from database import list_patients, add_patient, get_patient, update_patient, delete_patient, log_audit_action
from utils import requires_login, requires_role, get_current_user, get_client_ip, format_cedula

patients_bp = Blueprint("patients_bp", __name__)

@patients_bp.route("/api/patients", methods=["GET"])
@requires_login
def api_get_patients():
    search   = (request.args.get("search") or "").strip()
    patients = list_patients(search or None)
    return jsonify({"success": True, "patients": patients})

@patients_bp.route("/api/patients", methods=["POST"])
@requires_login
@requires_role("doctor", "admin")
def api_save_patient():
    data         = request.json or {}
    cedula       = format_cedula((data.get("cedula") or "").strip())
    name         = (data.get("name") or "").strip()
    dob          = data.get("dob") or "1990-01-01"
    gender       = data.get("gender") or "Otro"
    antecedentes = data.get("antecedentes") or {}
    phone        = (data.get("phone") or "").strip() or None
    blood_type   = (data.get("blood_type") or "").strip() or None

    if not cedula:
        return jsonify({"success": False, "error": "La cédula del paciente es obligatoria."}), 400
    if not name:
        return jsonify({"success": False, "error": "El nombre completo del paciente es requerido."}), 400

    u = get_current_user()
    registered_by = u.get("id")

    if add_patient(cedula, name, dob, gender, antecedentes, phone, blood_type, registered_by):
        log_audit_action(
            username=u.get("username"), action="CREATE", entity="Patient",
            details=f"Registrado paciente '{name}' cédula '{cedula}'",
            ip_address=get_client_ip(), user_id=u.get("id")
        )
        return jsonify({"success": True, "patient": {
            "cedula": cedula, "name": name, "dob": dob, "gender": gender
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
@requires_role("admin")
def api_update_patient(patient_id):
    data       = request.json or {}
    cedula     = format_cedula((data.get("cedula") or "").strip()) or None
    name       = (data.get("name") or "").strip() or None
    dob        = data.get("dob") or None
    gender     = (data.get("gender") or "").strip() or None
    phone      = (data.get("phone") or "").strip() or None
    blood_type = (data.get("blood_type") or "").strip() or None
    antecedentes = data.get("antecedentes")

    if not update_patient(patient_id, cedula, name, dob, gender, phone, blood_type, antecedentes):
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
