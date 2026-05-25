from flask import Blueprint, request, jsonify
from database import list_records, add_record, list_clinical_history, get_clinical_report
from utils import requires_login, get_current_user, requires_role

history_bp = Blueprint("history_bp", __name__)

@history_bp.route("/api/records", methods=["GET"])
@requires_login
def api_get_records():
    records = list_records()
    return jsonify({"success": True, "records": records})

@history_bp.route("/api/records/<int:record_id>", methods=["GET"])
@requires_login
def api_get_record(record_id):
    report = get_clinical_report(record_id)
    if report is None:
        return jsonify({"success": False, "error": "Reporte no encontrado."}), 404
    return jsonify({"success": True, "clinical_report": report})

@history_bp.route("/api/records", methods=["POST"])
@requires_login
@requires_role("doctor")
def api_add_record():
    data = request.json or {}
    patient_id = data.get("patient_id")
    diagnosis  = data.get("diagnosis")
    notes      = data.get("notes", "")

    if not patient_id or not diagnosis:
        return jsonify({"success": False, "error": "Faltan datos obligatorios"}), 400

    doctor_id = get_current_user()["id"]
    record = {
        "patient_id": patient_id,
        "doctor_username": get_current_user()["username"],
        "diagnosis": diagnosis,
        "notes": notes
    }
    if add_record(record):
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Error al guardar registro"}), 500

@history_bp.route("/api/clinical_history", methods=["GET"])
@requires_login
def api_clinical_history():
    history = list_clinical_history()
    return jsonify({"success": True, "history": history})
