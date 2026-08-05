from flask import Blueprint, request, jsonify
from utils import requires_login, get_current_user, get_client_ip
from database import (
    get_all_clinic_settings, log_audit_action, list_users,
    get_report_patient, get_report_waiting_time,
    get_report_model_performance, get_report_doctor_activity, get_report_billing,
    get_report_prescriptions, get_report_recurrent_patients,
    get_report_ai_comparison
)

reports_bp = Blueprint("reports_bp", __name__)

def _get_doctor_id_from_request():
    """
    Resuelve y valida el doctor_id basado en el rol del usuario actual y los permisos.
    Retorna (doctor_id, error_response). Si error_response no es None, se debe abortar la peticion.
    """
    u = get_current_user()
    role = u.get("role")
    
    if role == "doctor":
        # El doctor SIEMPRE ve sus propios reportes, ignora el parámetro de URL
        return u.get("id"), None
        
    requested_doctor_id = request.args.get("doctor_id", type=int)
    
    if role == "admin":
        if requested_doctor_id:
            log_audit_action(
                username=u.get("username"), action="VIEW_REPORT", entity="User",
                entity_id=str(requested_doctor_id), details="Admin visualizando reportes de doctor",
                ip_address=get_client_ip(), user_id=u.get("id")
            )
        return requested_doctor_id, None
        
    if role == "secretaria":
        settings = get_all_clinic_settings()
        if str(settings.get("enable_secretaria_reports", "0")) != "1":
            return None, (jsonify({"success": False, "error": "Acceso denegado a reportes."}), 403)
        if requested_doctor_id:
            log_audit_action(
                username=u.get("username"), action="VIEW_REPORT", entity="User",
                entity_id=str(requested_doctor_id), details="Secretaria visualizando reportes de doctor",
                ip_address=get_client_ip(), user_id=u.get("id")
            )
        return requested_doctor_id, None

    return None, (jsonify({"success": False, "error": "Rol no soportado para reportes."}), 403)


@reports_bp.route("/api/reports/doctor-list", methods=["GET"])
@requires_login
def api_reports_doctor_list():
    u = get_current_user()
    if u.get("role") == "doctor":
        return jsonify({"success": False, "error": "No disponible para doctores."}), 403
    
    if u.get("role") == "secretaria":
        settings = get_all_clinic_settings()
        if str(settings.get("enable_secretaria_reports", "0")) != "1":
            return jsonify({"success": False, "error": "Acceso denegado."}), 403
            
    users = list_users()
    doctors = [{"id": doc["id"], "full_name": doc["full_name"], "especialidad": doc.get("especialidad")} 
               for doc in users if doc["role"] == "doctor" and doc["is_active"]]
    
    return jsonify({"success": True, "doctors": doctors})

@reports_bp.route("/api/reports/agenda", methods=["GET"])
@requires_login
def api_reports_agenda():
    doctor_id, error = _get_doctor_id_from_request()
    if error: return error
    
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    data = get_report_waiting_time(doctor_id, date_from, date_to)
    return jsonify({"success": True, "agenda": data})

@reports_bp.route("/api/reports/patient/<int:patient_id>", methods=["GET"])
@requires_login
def api_reports_patient(patient_id):
    doctor_id, error = _get_doctor_id_from_request()
    if error: return error
    
    data = get_report_patient(patient_id, doctor_id)
    return jsonify({"success": True, "patient_history": data})

@reports_bp.route("/api/reports/recurrent", methods=["GET"])
@requires_login
def api_reports_recurrent():
    doctor_id, error = _get_doctor_id_from_request()
    if error: return error
    
    min_visits = request.args.get("min_visits", 2, type=int)
    data = get_report_recurrent_patients(doctor_id, min_visits)
    return jsonify({"success": True, "recurrent_patients": data})

@reports_bp.route("/api/reports/ai-comparison", methods=["GET"])
@requires_login
def api_reports_ai_comparison():
    doctor_id, error = _get_doctor_id_from_request()
    if error: return error
    
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    
    performance = get_report_model_performance(doctor_id, date_from, date_to)
    refutations = get_report_ai_comparison(doctor_id)
    
    return jsonify({
        "success": True, 
        "performance": performance,
        "refutations": refutations
    })

@reports_bp.route("/api/reports/prescriptions", methods=["GET"])
@requires_login
def api_reports_prescriptions():
    doctor_id, error = _get_doctor_id_from_request()
    if error: return error
    
    limit = request.args.get("limit", 100, type=int)
    data = get_report_prescriptions(doctor_id, limit)
    return jsonify({"success": True, "prescriptions": data})

@reports_bp.route("/api/reports/activity", methods=["GET"])
@requires_login
def api_reports_activity():
    doctor_id, error = _get_doctor_id_from_request()
    if error: return error
    
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    
    data = get_report_doctor_activity(date_from, date_to)
    if doctor_id is not None:
        data = [d for d in data if d["doctor_id"] == doctor_id]
        
    return jsonify({"success": True, "activity": data})

@reports_bp.route("/api/reports/billing", methods=["GET"])
@requires_login
def api_reports_billing():
    doctor_id, error = _get_doctor_id_from_request()
    if error: return error
    
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    invoice_type = request.args.get("invoice_type")
    
    data = get_report_billing(date_from, date_to, invoice_type, doctor_id=doctor_id)
    return jsonify({"success": True, "billing": data})

@reports_bp.route("/api/reports/epidemiology", methods=["GET"])
@requires_login
def api_reports_epidemiology():
    doctor_id, error = _get_doctor_id_from_request()
    if error: return error
    
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    
    from database import get_epidemiology_report
    data = get_epidemiology_report(date_from=date_from, date_to=date_to, doctor_id=doctor_id)
    return jsonify(data)
