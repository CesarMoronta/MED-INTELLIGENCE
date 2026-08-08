from flask import Blueprint, request, jsonify
from database import (list_appointments, create_appointment, update_appointment_status,
                      reschedule_appointment, update_appointment, get_waiting_room,
                      mark_patient_arrived, confirm_appointment, get_patient,
                      get_appointment, check_appointment_clash, get_clinic_working_hours,
                      get_connection, log_audit_action)
from utils import requires_login, requires_role, get_current_user, get_client_ip

appointments_bp = Blueprint("appointments_bp", __name__)


@appointments_bp.route("/api/appointments", methods=["GET"])
@requires_login
def api_list_appointments():
    user = get_current_user()
    # Si es doctor, solo ve sus citas. Si es secretaria/admin, ve todas (o filtra por doctor).
    doctor_id = user["id"] if user["role"] == "doctor" else None

    # Permitir filtrar explícitamente (solo para admin/secretaria)
    req_doctor_id = request.args.get("doctor_id")
    if req_doctor_id and user["role"] != "doctor":
        doctor_id = int(req_doctor_id)

    # Filtrar por hoy si lo piden
    date_filter = None
    if request.args.get("today") == "1":
        from datetime import date
        date_filter = str(date.today())

    apps = list_appointments(doctor_id=doctor_id, date_filter=date_filter)
    return jsonify({"success": True, "appointments": apps})


def validate_appointment_availability(doctor_id, scheduled_date, scheduled_time):
    from datetime import datetime
    
    # 1. Validar jornada laboral de la clínica
    try:
        day_num = datetime.strptime(str(scheduled_date), "%Y-%m-%d").isoweekday()
    except ValueError:
        return "Fecha inválida."
        
    clinic_hours = get_clinic_working_hours()
    day_config = next((h for h in clinic_hours if h["day_of_week"] == day_num), None)
    if not day_config or not day_config["is_active"]:
        return "El consultorio está cerrado el día de la semana seleccionado."
        
    start_time_str = day_config["start_time"]
    end_time_str = day_config["end_time"]
    
    # Normalizar hora de la cita a HH:MM
    app_time_str = str(scheduled_time)[:5]
    
    if not (start_time_str <= app_time_str <= end_time_str):
        return f"La hora seleccionada ({app_time_str}) está fuera de la jornada laboral del consultorio para este día ({start_time_str} - {end_time_str})."
        
    # 2. Validar bloqueos específicos del doctor
    conn = get_connection()
    cursor = conn.cursor()
    try:
        s_time = app_time_str + ":00"
        cursor.execute("""
            SELECT id, reason, start_time, end_time 
            FROM dbo.doctor_blocked_slots
            WHERE doctor_id = ? 
              AND CAST(blocked_date AS DATE) = CAST(? AS DATE)
              AND CAST(? AS TIME) >= start_time 
              AND CAST(? AS TIME) <= end_time
        """, doctor_id, scheduled_date, s_time, s_time)
        block = cursor.fetchone()
        if block:
            reason = block[1] or "No especificada"
            return f"El doctor no está disponible en este horario. Motivo: {reason} (Bloqueado de {str(block[2])[:5]} a {str(block[3])[:5]})."
    finally:
        cursor.close()
        conn.close()
        
    return None

@appointments_bp.route("/api/appointments", methods=["POST"])
@requires_login
@requires_role("admin", "secretaria")
def api_create_appointment():
    data = request.json or {}
    patient_id     = data.get("patient_id")
    doctor_id      = data.get("doctor_id")
    scheduled_date = data.get("scheduled_date")
    scheduled_time = data.get("scheduled_time")
    notes          = data.get("notes")
    parent_app_id  = data.get("parent_appointment_id")

    if not all([patient_id, doctor_id, scheduled_date, scheduled_time]):
        return jsonify({"success": False, "error": "Faltan campos requeridos."}), 400

    from datetime import datetime
    try:
        patient_id = int(patient_id)
        doctor_id  = int(doctor_id)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "ID de paciente y doctor deben ser numéricos."}), 400

    try:
        datetime.strptime(str(scheduled_date), "%Y-%m-%d")
    except ValueError:
        return jsonify({"success": False, "error": "Formato de fecha inválido. Debe ser AAAA-MM-DD."}), 400

    try:
        time_str = str(scheduled_time).strip()
        if len(time_str) == 5:
            datetime.strptime(time_str, "%H:%M")
        elif len(time_str) == 8:
            datetime.strptime(time_str, "%H:%M:%S")
        else:
            raise ValueError()
    except ValueError:
        return jsonify({"success": False, "error": "Formato de hora inválido. Debe ser HH:MM."}), 400

    # Evitar agendar en el pasado
    from datetime import date
    try:
        app_date = datetime.strptime(str(scheduled_date), "%Y-%m-%d").date()
        if app_date < date.today():
            return jsonify({"success": False, "error": "No se puede agendar una cita para una fecha en el pasado."}), 400
    except ValueError:
        pass

    # Bloquear cita si paciente fallecido
    patient = get_patient(patient_id)
    if patient and patient.get("vital_status") == "Fallecido":
        return jsonify({"success": False, "error": "No se puede agendar una cita para un paciente fallecido."}), 409

    # Validar disponibilidad
    err = validate_appointment_availability(doctor_id, scheduled_date, scheduled_time)
    if err:
        return jsonify({"success": False, "error": err}), 400

    app_id = create_appointment(patient_id, doctor_id, scheduled_date, scheduled_time, notes, parent_app_id)
    u = get_current_user()
    patient_name = patient.get("name") if patient else "Desconocido"
    log_audit_action(
        username=u.get("username"), action="CREATE", entity="Appointment",
        entity_id=str(app_id),
        details=f"Agendó cita ID {app_id} para el paciente '{patient_name}' (ID: {patient_id}) con doctor ID {doctor_id} el {scheduled_date} a las {scheduled_time}",
        ip_address=get_client_ip(), user_id=u.get("id")
    )
    return jsonify({"success": True, "appointment_id": app_id, "message": "Cita agendada."})


@appointments_bp.route("/api/appointments/<int:app_id>", methods=["PUT"])
@requires_login
def api_update_appointment(app_id):
    user = get_current_user()
    if user["role"] not in ["admin", "secretaria", "doctor"]:
        return jsonify({"success": False, "error": "No autorizado."}), 403

    current_app = get_appointment(app_id)
    if not current_app:
        return jsonify({"success": False, "error": "Cita no encontrada."}), 404

    if current_app["status"] == "completada":
        return jsonify({"success": False, "error": "No se pueden editar citas completadas."}), 400
    if current_app["status"] == "cancelada":
        return jsonify({"success": False, "error": "No se pueden editar citas canceladas."}), 400

    data           = request.json or {}
    doctor_id      = data.get("doctor_id")
    scheduled_date = data.get("scheduled_date")
    scheduled_time = data.get("scheduled_time")
    status         = data.get("status")
    notes          = data.get("notes")
    confirmed      = data.get("confirmed")  # para sala de espera

    if scheduled_date:
        from datetime import datetime, date
        try:
            datetime.strptime(str(scheduled_date), "%Y-%m-%d")
        except ValueError:
            return jsonify({"success": False, "error": "Formato de fecha inválido. Debe ser AAAA-MM-DD."}), 400
        
        try:
            app_date = datetime.strptime(str(scheduled_date), "%Y-%m-%d").date()
            if app_date < date.today():
                return jsonify({"success": False, "error": "No se puede reprogramar una cita para una fecha en el pasado."}), 400
        except ValueError:
            pass

    if scheduled_time:
        from datetime import datetime
        try:
            time_str = str(scheduled_time).strip()
            if len(time_str) == 5:
                datetime.strptime(time_str, "%H:%M")
            elif len(time_str) == 8:
                datetime.strptime(time_str, "%H:%M:%S")
            else:
                raise ValueError()
        except ValueError:
            return jsonify({"success": False, "error": "Formato de hora inválido. Debe ser HH:MM."}), 400

    # Actualización completa (agenda) vs parcial (sala de espera / solo estado)
    if doctor_id and scheduled_date and scheduled_time and status:
        err = validate_appointment_availability(doctor_id, scheduled_date, scheduled_time)
        if err:
            return jsonify({"success": False, "error": err}), 400
        updated = update_appointment(app_id, doctor_id, scheduled_date, scheduled_time, status, notes)
    elif status or confirmed is not None:
        # Actualización parcial: solo estado / confirmación
        updated = update_appointment_status(app_id, status or "en_curso")
        if confirmed and updated:
            confirm_appointment(app_id, notes or "")
    else:
        return jsonify({"success": False, "error": "Faltan campos requeridos."}), 400

    if updated:
        u = get_current_user()
        log_audit_action(
            username=u.get("username"), action="UPDATE", entity="Appointment",
            entity_id=str(app_id),
            details=f"Actualizó detalles de cita ID {app_id} (Estado: {status or current_app.get('status')})",
            ip_address=get_client_ip(), user_id=u.get("id")
        )
        return jsonify({"success": True, "message": "Cita actualizada."})
    return jsonify({"success": False, "error": "Cita no encontrada."}), 404



@appointments_bp.route("/api/appointments/<int:app_id>/status", methods=["POST"])
@requires_login
def api_update_appointment_status(app_id):
    data   = request.json or {}
    status = data.get("status")
    if status not in ["abierta", "en_curso", "completada", "cancelada"]:
        return jsonify({"success": False, "error": "Estado inválido."}), 400

    user = get_current_user()
    if status == "abierta":
        if user["role"] not in ["admin", "secretaria"]:
            return jsonify({"success": False, "error": "Solo administradores o secretarias pueden activar citas."}), 403
        
        current_app = get_appointment(app_id)
        if not current_app:
            return jsonify({"success": False, "error": "Cita no encontrada."}), 404
        
        if check_appointment_clash(app_id):
            return jsonify({
                "success": False, 
                "error": "No se puede activar la cita porque choca con otra cita activa programada para el mismo doctor a esa hora."
            }), 409

    updated = update_appointment_status(app_id, status)
    if updated:
        u = get_current_user()
        log_audit_action(
            username=u.get("username"), action="UPDATE", entity="Appointment",
            entity_id=str(app_id),
            details=f"Actualizó estado de cita ID {app_id} a '{status}'",
            ip_address=get_client_ip(), user_id=u.get("id")
        )
        return jsonify({"success": True, "message": "Estado actualizado."})
    return jsonify({"success": False, "error": "Cita no encontrada."}), 404


@appointments_bp.route("/api/appointments/<int:app_id>/reschedule", methods=["PUT"])
@requires_login
@requires_role("admin", "secretaria")
def api_reschedule_appointment(app_id):
    current_app = get_appointment(app_id)
    if not current_app:
        return jsonify({"success": False, "error": "Cita no encontrada."}), 404

    if current_app["status"] == "completada":
        return jsonify({"success": False, "error": "No se pueden reprogramar citas completadas."}), 400
    if current_app["status"] == "cancelada":
        return jsonify({"success": False, "error": "No se pueden reprogramar citas canceladas."}), 400

    data     = request.json or {}
    new_date = data.get("scheduled_date")
    new_time = data.get("scheduled_time")

    if not new_date or not new_time:
        return jsonify({"success": False, "error": "Fecha y hora son requeridas."}), 400

    err = validate_appointment_availability(current_app["doctor_id"], new_date, new_time)
    if err:
        return jsonify({"success": False, "error": err}), 400

    updated = reschedule_appointment(app_id, new_date, new_time)
    if updated:
        u = get_current_user()
        log_audit_action(
            username=u.get("username"), action="UPDATE", entity="Appointment",
            entity_id=str(app_id),
            details=f"Reprogramó cita ID {app_id} para el {new_date} a las {new_time}",
            ip_address=get_client_ip(), user_id=u.get("id")
        )
        return jsonify({"success": True, "message": "Cita reprogramada."})
    return jsonify({"success": False, "error": "Cita no encontrada."}), 404


# ─── Sala de Espera ───────────────────────────────────────────────────────────

@appointments_bp.route("/api/waiting-room", methods=["GET"])
@requires_login
def api_waiting_room():
    """Citas del día con estado de llegada del paciente."""
    user      = get_current_user()
    doctor_id = user["id"] if user["role"] == "doctor" else request.args.get("doctor_id", type=int)
    room      = get_waiting_room(doctor_id=doctor_id)
    return jsonify({"success": True, "waiting_room": room})


@appointments_bp.route("/api/appointments/<int:app_id>/arrive", methods=["POST"])
@requires_login
@requires_role("admin", "secretaria")
def api_mark_arrived(app_id):
    """Marca que el paciente llegó al consultorio."""
    ok = mark_patient_arrived(app_id)
    if ok:
        u = get_current_user()
        log_audit_action(
            username=u.get("username"), action="UPDATE", entity="Appointment",
            entity_id=str(app_id),
            details=f"Marcó llegada del paciente para la cita ID {app_id}",
            ip_address=get_client_ip(), user_id=u.get("id")
        )
        return jsonify({"success": True, "message": "Paciente registrado como llegado."})
    return jsonify({"success": False, "error": "Cita no encontrada."}), 404


@appointments_bp.route("/api/appointments/<int:app_id>/confirm", methods=["POST"])
@requires_login
@requires_role("admin", "secretaria")
def api_confirm_appointment(app_id):
    """Confirma una cita (llamó y confirmó)."""
    data  = request.json or {}
    notes = data.get("notes", "")
    ok    = confirm_appointment(app_id, notes)
    if ok:
        u = get_current_user()
        log_audit_action(
            username=u.get("username"), action="UPDATE", entity="Appointment",
            entity_id=str(app_id),
            details=f"Confirmó cita ID {app_id}",
            ip_address=get_client_ip(), user_id=u.get("id")
        )
        return jsonify({"success": True, "message": "Cita confirmada."})
    return jsonify({"success": False, "error": "Cita no encontrada."}), 404
