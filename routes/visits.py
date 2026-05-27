from flask import Blueprint, request, jsonify
from database import list_visits, create_visit, get_visit, save_visit_tests, add_prescription, get_prescriptions_for_visit
from utils import requires_login, requires_role, get_current_user

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

    if not patient_id:
        return jsonify({"success": False, "error": "El ID del paciente es obligatorio."}), 400
    if visit_type not in ["emergencia", "consulta"]:
        return jsonify({"success": False, "error": "Tipo de visita inválido."}), 400
    if visit_type == "emergencia" and not motivo_emergencia:
        return jsonify({"success": False, "error": "El motivo de emergencia es obligatorio."}), 400

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
        sintomas=sintomas
    )

    if not visit_id:
        return jsonify({"success": False, "error": "Error al crear la visita."}), 500

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
    return jsonify({"success": True, "prescription_id": pid, "message": "Receta añadida."})
