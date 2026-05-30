from flask import Blueprint, request, jsonify
from database import list_records, add_record, list_clinical_history, get_clinical_report
from utils import requires_login, get_current_user, requires_role

history_bp = Blueprint("history_bp", __name__)


@history_bp.route("/api/records", methods=["GET"])
@requires_login
def api_get_records():
    u = get_current_user()
    # Secretaria no puede ver el historial clínico
    if u.get("role") == "secretaria":
        return jsonify({"success": False, "error": "Permiso denegado."}), 403
    records = list_records()
    return jsonify({"success": True, "records": records})


@history_bp.route("/api/records/<int:record_id>", methods=["GET"])
@requires_login
def api_get_record(record_id):
    u = get_current_user()
    if u.get("role") == "secretaria":
        return jsonify({"success": False, "error": "Permiso denegado."}), 403
    report = get_clinical_report(record_id)
    if report is None:
        return jsonify({"success": False, "error": "Reporte no encontrado."}), 404
    return jsonify({"success": True, "clinical_report": report})


@history_bp.route("/api/records", methods=["POST"])
@requires_login
@requires_role("doctor", "admin")
def api_add_record():
    u = get_current_user()
    data = request.json or {}
    patient_id = data.get("patient_id")
    diagnosis  = data.get("diagnosis")
    notes      = data.get("notes", "")

    if not patient_id or not diagnosis:
        return jsonify({"success": False, "error": "Faltan datos obligatorios"}), 400

    record = {
        "patient_id": patient_id,
        "doctor_username": u["username"],
        "diagnosis": diagnosis,
        "notes": notes
    }
    if add_record(record):
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Error al guardar registro"}), 500


@history_bp.route("/api/clinical_history", methods=["GET"])
@requires_login
def api_clinical_history():
    u = get_current_user()
    # Secretaria no puede ver el historial clínico
    if u.get("role") == "secretaria":
        return jsonify({"success": False, "error": "Permiso denegado."}), 403
    # Doctor solo ve su propio historial
    doctor_id = u.get("id") if u.get("role") == "doctor" else None
    history = list_clinical_history(doctor_id=doctor_id)
    return jsonify({"success": True, "history": history})


@history_bp.route("/api/history", methods=["GET"])
@requires_login
def api_history_alias():
    """Alias usado por el modal de paciente en el frontend.
    Soporta: ?patient_id=X&limit=N&alert=rojo
    """
    u = get_current_user()
    if u.get("role") == "secretaria":
        return jsonify({"success": False, "error": "Permiso denegado."}), 403

    patient_id  = request.args.get("patient_id", type=int)
    limit       = request.args.get("limit", 50, type=int)
    alert_level = request.args.get("alert")   # "rojo", "amarillo", "verde"
    doctor_id   = u.get("id") if u.get("role") == "doctor" else None

    records = list_clinical_history(
        doctor_id  = doctor_id,
        patient_id = patient_id,
        alert_level= alert_level,
        limit      = limit
    )
    return jsonify({"success": True, "records": records})
