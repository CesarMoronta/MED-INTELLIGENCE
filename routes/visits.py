from flask import Blueprint, request, jsonify
from database import (list_visits, create_visit, get_visit, save_visit_tests,
                      add_prescription, get_prescriptions_for_visit, get_patient,
                      get_user_by_id, log_audit_action)
from extensions import gemini_layer
from utils import requires_login, requires_role, get_current_user, get_client_ip

visits_bp = Blueprint("visits_bp", __name__)

@visits_bp.route("/api/visits", methods=["GET"])
@requires_login
def api_list_visits():
    patient_id = request.args.get("patient_id", type=int)
    visits = list_visits(patient_id=patient_id)
    return jsonify({"success": True, "visits": visits})

@visits_bp.route("/api/visits", methods=["POST"])
@requires_login
@requires_role("doctor", "admin")
def api_create_visit():
    data               = request.json or {}
    patient_id         = data.get("patient_id")
    visit_type         = (data.get("visit_type") or "consulta").lower()
    motivo_consulta    = (data.get("motivo_consulta") or "").strip() or None
    motivo_emergencia  = (data.get("motivo_emergencia") or "").strip() or None
    doctor_notes       = (data.get("doctor_notes") or "").strip() or None
    constantes         = data.get("constantes") or {}
    sintomas           = data.get("sintomas") or {}
    appointment_id     = data.get("appointment_id")

    if not patient_id:
        return jsonify({"success": False, "error": "El ID del paciente es obligatorio."}), 400
    try:
        patient_id = int(patient_id)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "El ID del paciente debe ser numérico."}), 400
    if visit_type not in ["emergencia", "consulta"]:
        return jsonify({"success": False, "error": "Tipo de visita inválido."}), 400
    if visit_type == "emergencia" and not motivo_emergencia:
        return jsonify({"success": False, "error": "El motivo de emergencia es obligatorio."}), 400

    # Bloquear visita si paciente fallecido
    patient_check = get_patient(patient_id)
    if patient_check and patient_check.get("vital_status") == "Fallecido":
        return jsonify({"success": False, "error": "No se puede abrir una consulta para un paciente fallecido."}), 409

    u = get_current_user()
    doctor_id = u.get("id")

    visit_id = create_visit(
        patient_id=patient_id,
        doctor_id=doctor_id,
        visit_type=visit_type,
        motivo_consulta=motivo_consulta,
        motivo_emergencia=motivo_emergencia,
        doctor_notes=doctor_notes,
        constantes=constantes,
        sintomas=sintomas,
        appointment_id=appointment_id
    )

    if not visit_id:
        return jsonify({"success": False, "error": "Error al crear la visita."}), 500

    patient_name = patient_check.get("name") if patient_check else "Desconocido"
    log_audit_action(
        username=u.get("username"), action="CREATE", entity="Visit",
        entity_id=str(visit_id),
        details=f"Inició una {visit_type} para el paciente '{patient_name}' (ID: {patient_id})",
        ip_address=get_client_ip(), user_id=u.get("id")
    )

    return jsonify({"success": True, "visit_id": visit_id})

@visits_bp.route("/api/visits/<int:visit_id>", methods=["GET"])
@requires_login
def api_get_visit(visit_id):
    visit = get_visit(visit_id)
    if not visit:
        return jsonify({"success": False, "error": "Visita no encontrada."}), 404
    
    # Obtener también las recetas
    visit["prescriptions"] = get_prescriptions_for_visit(visit_id)
    
    return jsonify({"success": True, "visit": visit})

@visits_bp.route("/api/visits/<int:visit_id>/tests", methods=["POST"])
@requires_login
@requires_role("doctor", "admin")
def api_save_tests(visit_id):
    data  = request.json or {}
    tests = data.get("tests", [])
    if save_visit_tests(visit_id, tests):
        u = get_current_user()
        log_audit_action(
            username=u.get("username"), action="UPDATE", entity="Visit",
            entity_id=str(visit_id),
            details=f"Guardó resultados de pruebas para la visita ID {visit_id}",
            ip_address=get_client_ip(), user_id=u.get("id")
        )
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "No se pudieron guardar las pruebas."}), 500

@visits_bp.route("/api/visits/<int:visit_id>/prescription", methods=["POST"])
@requires_login
@requires_role("doctor", "admin")
def api_add_prescription(visit_id):
    data = request.json or {}
    medication = data.get("medication")
    dosage = data.get("dosage")
    frequency = data.get("frequency")
    duration_days = data.get("duration_days")
    quantity = data.get("quantity")
    notes = data.get("notes")
    
    if not all([medication, dosage, frequency, duration_days, quantity]):
        return jsonify({"success": False, "error": "Faltan campos requeridos."}), 400
        
    pid = add_prescription(visit_id, medication, dosage, frequency, int(duration_days), int(quantity), notes)
    u = get_current_user()
    log_audit_action(
        username=u.get("username"), action="UPDATE", entity="Visit",
        entity_id=str(visit_id),
        details=f"Agregó receta médica (medicamento: {medication}) para la visita ID {visit_id}",
        ip_address=get_client_ip(), user_id=u.get("id")
    )
    return jsonify({"success": True, "prescription_id": pid, "message": "Receta añadida."})


@visits_bp.route("/api/visits/<int:visit_id>/prescription/generate-ai", methods=["POST"])
@requires_login
@requires_role("doctor", "admin")
def api_generate_prescription_ai(visit_id):
    # Verificar suscripción si es doctor
    u = get_current_user()
    if u.get("role") == "doctor":
        user_db = get_user_by_id(u["id"])
        if not user_db or not user_db.get("subscription_active"):
            return jsonify({
                "success": False,
                "error": "subscription_required",
                "message": "Se requiere una suscripción VIP activa de PayPal para usar la generación de recetas con IA."
            }), 403

    visit = get_visit(visit_id)
    if not visit:
        return jsonify({"success": False, "error": "Visita no encontrada."}), 404

    patient = get_patient(visit["patient_id"])
    if not patient:
        return jsonify({"success": False, "error": "Paciente no encontrado."}), 404

    # Recopilar contexto
    sintomas_activos = [s for s, pres in visit.get("sintomas", {}).items() if pres]
    antecedentes_activos = [a for a, pres in patient.get("antecedentes", {}).items() if pres]
    
    res = gemini_layer.generar_receta_con_ia(
        diagnostico=visit.get("diagnosis_primary") or "No especificado",
        motivo_consulta=visit.get("motivo_consulta") or "No especificado",
        doctor_notes=visit.get("doctor_notes") or "Ninguna",
        constantes=visit.get("constantes", {}),
        sintomas_activos=sintomas_activos,
        antecedentes_activos=antecedentes_activos,
        paciente_edad=patient.get("age", 30),
        paciente_genero=patient.get("gender", "Otro"),
        alert_level=visit.get("alert_level") or "Verde"
    )

    if res.get("fallback"):
        return jsonify({"success": False, "error": "El motor de IA está offline o no disponible."}), 503

    log_audit_action(
        username=u.get("username"), action="GENERATE_AI", entity="Visit",
        entity_id=str(visit_id),
        details=f"Generó receta médica asistida por IA para la visita ID {visit_id}",
        ip_address=get_client_ip(), user_id=u.get("id")
    )

    return jsonify({"success": True, "medications": res.get("medications", [])})

