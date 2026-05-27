from flask import Blueprint, request, jsonify
from database import list_appointments, create_appointment, update_appointment_status, reschedule_appointment
from utils import requires_login, requires_role, get_current_user

appointments_bp = Blueprint("appointments_bp", __name__)

@appointments_bp.route("/api/appointments", methods=["GET"])
@requires_login
def api_list_appointments():
    user = get_current_user()
    # Si es doctor, solo ve sus citas. Si es secretaria/admin, ve todas (o podemos filtrar).
    doctor_id = user["id"] if user["role"] == "doctor" else None
    
    # Permitir filtrar explícitamente
    req_doctor_id = request.args.get("doctor_id")
    if req_doctor_id and user["role"] != "doctor":
        doctor_id = int(req_doctor_id)
        
    apps = list_appointments(doctor_id=doctor_id)
    return jsonify({"success": True, "appointments": apps})

@appointments_bp.route("/api/appointments", methods=["POST"])
@requires_login
def api_create_appointment():
    user = get_current_user()
    if user["role"] not in ["admin", "secretaria"]:
        return jsonify({"success": False, "error": "No autorizado para agendar citas."}), 403
        
    data = request.json or {}
    patient_id = data.get("patient_id")
    doctor_id = data.get("doctor_id")
    scheduled_date = data.get("scheduled_date")
    scheduled_time = data.get("scheduled_time")
    notes = data.get("notes")
    
    if not all([patient_id, doctor_id, scheduled_date, scheduled_time]):
        return jsonify({"success": False, "error": "Faltan campos requeridos."}), 400
        
    app_id = create_appointment(patient_id, doctor_id, scheduled_date, scheduled_time, notes)
    return jsonify({"success": True, "appointment_id": app_id, "message": "Cita agendada."})

@appointments_bp.route("/api/appointments/<int:app_id>", methods=["PUT"])
@requires_login
def api_update_appointment(app_id):
    user = get_current_user()
    if user["role"] not in ["admin", "secretaria", "doctor"]:
        return jsonify({"success": False, "error": "No autorizado."}), 403
        
    data = request.json or {}
    doctor_id = data.get("doctor_id")
    scheduled_date = data.get("scheduled_date")
    scheduled_time = data.get("scheduled_time")
    status = data.get("status")
    notes = data.get("notes")
    
    if not all([doctor_id, scheduled_date, scheduled_time, status]):
        return jsonify({"success": False, "error": "Faltan campos requeridos."}), 400
        
    from database import update_appointment
    updated = update_appointment(app_id, doctor_id, scheduled_date, scheduled_time, status, notes)
    if updated:
        return jsonify({"success": True, "message": "Cita actualizada."})
    return jsonify({"success": False, "error": "Cita no encontrada."}), 404

@appointments_bp.route("/api/appointments/<int:app_id>/status", methods=["POST"])
@requires_login
def api_update_appointment_status(app_id):
    data = request.json or {}
    status = data.get("status")
    if status not in ["abierta", "en_curso", "completada", "cancelada"]:
        return jsonify({"success": False, "error": "Estado inválido."}), 400
        
    updated = update_appointment_status(app_id, status)
    if updated:
        return jsonify({"success": True, "message": "Estado actualizado."})
    return jsonify({"success": False, "error": "Cita no encontrada."}), 404

@appointments_bp.route("/api/appointments/<int:app_id>/reschedule", methods=["PUT"])
@requires_login
def api_reschedule_appointment(app_id):
    user = get_current_user()
    if user["role"] not in ["admin", "secretaria"]:
        return jsonify({"success": False, "error": "No autorizado."}), 403

    data = request.json or {}
    new_date = data.get("scheduled_date")
    new_time = data.get("scheduled_time")

    if not new_date or not new_time:
        return jsonify({"success": False, "error": "Fecha y hora son requeridas."}), 400

    updated = reschedule_appointment(app_id, new_date, new_time)
    if updated:
        return jsonify({"success": True, "message": "Cita reprogramada."})
    return jsonify({"success": False, "error": "Cita no encontrada."}), 404
