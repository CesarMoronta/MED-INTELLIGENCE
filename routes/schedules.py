from flask import Blueprint, request, jsonify
from database import (
    get_clinic_working_hours,
    save_clinic_working_hours,
    get_doctor_blocked_slots,
    add_doctor_blocked_slot,
    delete_doctor_blocked_slot,
    get_connection
)
from utils import requires_login, requires_role, get_current_user

schedules_bp = Blueprint("schedules_bp", __name__)

@schedules_bp.route("/api/schedules/clinic", methods=["GET"])
@requires_login
def api_get_clinic_hours():
    try:
        hours = get_clinic_working_hours()
        return jsonify({"success": True, "hours": hours})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@schedules_bp.route("/api/schedules/clinic", methods=["POST"])
@requires_login
@requires_role("admin", "secretaria")
def api_save_clinic_hours():
    data = request.json or {}
    hours_list = data.get("hours")
    if not hours_list or not isinstance(hours_list, list):
        return jsonify({"success": False, "error": "Se requiere una lista de horarios."}), 400
    
    try:
        success = save_clinic_working_hours(hours_list)
        if success:
            return jsonify({"success": True, "message": "Jornada laboral de la clínica actualizada."})
        return jsonify({"success": False, "error": "Error al guardar horarios."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@schedules_bp.route("/api/schedules/doctor/<int:doctor_id>/blocked", methods=["GET"])
@requires_login
def api_get_doctor_blocked(doctor_id):
    try:
        slots = get_doctor_blocked_slots(doctor_id)
        return jsonify({"success": True, "slots": slots})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@schedules_bp.route("/api/schedules/doctor/blocked", methods=["POST"])
@requires_login
def api_add_doctor_blocked():
    data = request.json or {}
    doctor_id    = data.get("doctor_id")
    blocked_date = data.get("blocked_date")
    start_time   = data.get("start_time")
    end_time     = data.get("end_time")
    reason       = (data.get("reason") or "").strip()

    if not all([doctor_id, blocked_date, start_time, end_time]):
        return jsonify({"success": False, "error": "Faltan campos obligatorios."}), 400

    u = get_current_user()
    try:
        doctor_id = int(doctor_id)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "El ID del doctor debe ser numérico."}), 400

    # Si es doctor, solo puede bloquear su propio horario
    if u.get("role") == "doctor" and u.get("id") != doctor_id:
        return jsonify({"success": False, "error": "Permiso denegado. No puedes bloquear el horario de otro doctor."}), 403

    created_by_doctor = (u.get("role") == "doctor")

    try:
        add_doctor_blocked_slot(
            doctor_id=doctor_id,
            blocked_date=blocked_date,
            start_time=start_time,
            end_time=end_time,
            reason=reason,
            created_by_doctor=created_by_doctor
        )
        return jsonify({"success": True, "message": "Horario bloqueado con éxito."})
    except Exception as e:
        # El mensaje de la excepción ya contiene los detalles de la cita que choca
        return jsonify({"success": False, "error": str(e)}), 400

@schedules_bp.route("/api/schedules/doctor/blocked/<int:slot_id>", methods=["DELETE"])
@requires_login
def api_delete_doctor_blocked(slot_id):
    u = get_current_user()
    
    # Si es doctor, verificar que el bloqueo le pertenezca a él
    if u.get("role") == "doctor":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT doctor_id FROM dbo.doctor_blocked_slots WHERE id = ?", slot_id)
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row or row[0] != u.get("id"):
            return jsonify({"success": False, "error": "Permiso denegado. Este bloqueo no te pertenece."}), 403

    try:
        success = delete_doctor_blocked_slot(slot_id)
        if success:
            return jsonify({"success": True, "message": "Bloqueo eliminado."})
        return jsonify({"success": False, "error": "El bloqueo no existe o ya fue eliminado."}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
