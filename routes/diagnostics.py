from flask import Blueprint, request, jsonify
from extensions import engine, gemini_layer
from database import save_diagnosis, save_visit_tests, get_medical_tests
from diagnostic_engine import OfflineAIEngine, CLINICAL_METADATA
from utils import requires_login, get_current_user

diagnostics_bp = Blueprint("diagnostics_bp", __name__)


def _block_secretaria():
    """Retorna 403 si el usuario actual es secretaria."""
    from utils import get_current_user
    u = get_current_user()
    if u.get("role") == "secretaria":
        return jsonify({"success": False, "error": "Permiso denegado."}), 403
    return None


@diagnostics_bp.route("/api/diagnose/preliminar", methods=["POST"])
@requires_login
def api_diagnose_preliminar():
    blocked = _block_secretaria()
    if blocked:
        return blocked

    data         = request.json or {}
    antecedentes = data.get("antecedentes", {})
    sintomas     = data.get("sintomas", {})
    constantes   = data.get("constantes", {})

    edad        = int(constantes.get("edad") or data.get("edad") or 30)
    temperatura = float(constantes.get("temperatura") or data.get("temperatura") or 37.0)
    spo2        = int(constantes.get("spo2") or data.get("spo2") or 98)
    pas         = int(constantes.get("pas") or data.get("pas") or 120)
    pad         = int(constantes.get("pad") or data.get("pad") or 80)
    fc          = int(constantes.get("fc") or data.get("fc") or 80)
    fr          = int(constantes.get("fr") or data.get("fr") or 16)

    constantes_dict = {
        "edad": edad, "temperatura": temperatura, "spo2": spo2,
        "pas": pas, "pad": pad, "fc": fc, "fr": fr
    }

    custom_priors       = data.get("custom_priors")
    custom_conditionals = data.get("custom_conditionals")

    try:
        probabilidades, pasos = engine.calcular_diagnostico_preliminar(
            constantes_dict, antecedentes, sintomas,
            custom_priors, custom_conditionals
        )
        diagnostico_preliminar = max(probabilidades, key=probabilidades.get)
        meta      = CLINICAL_METADATA.get(diagnostico_preliminar, {})
        raw_tests = meta.get("clinical_tests", [])
        clean_tests = []
        for t in raw_tests:
            if "**" in t:
                parts = t.split("**")
                clean_tests.append(parts[1].replace(":", "").strip() if len(parts) > 1 else t)
            else:
                clean_tests.append(t)

        return jsonify({
            "success": True,
            "probabilities": probabilidades,
            "diagnosis_preliminar": diagnostico_preliminar,
            "tests_sugeridos": clean_tests,
            "pasos_calculo": pasos
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@diagnostics_bp.route("/api/diagnose/gemini-analisis", methods=["POST"])
@requires_login
def api_diagnose_gemini_analisis():
    """
    Endpoint de enriquecimiento post-Bayes con Gemini AI.
    Recibe las probabilidades bayesianas del preliminar y devuelve:
    - Validación clínica del top diagnóstico
    - Síntomas adicionales sugeridos que explorar
    - Alertas clínicas detectadas por Gemini
    - Nivel de confianza con justificación
    """
    blocked = _block_secretaria()
    if blocked:
        return blocked

    data         = request.json or {}
    probs_bayes  = data.get("probabilities", {})
    sintomas     = data.get("sintomas", {})
    constantes   = data.get("constantes", {})
    antecedentes = data.get("antecedentes", {})

    if not probs_bayes:
        return jsonify({"success": False, "error": "Se requieren probabilidades bayesianas."}), 400

    try:
        resultado = gemini_layer.enriquecer_diagnostico_preliminar(
            probs_bayes=probs_bayes,
            sintomas=sintomas,
            constantes=constantes,
            antecedentes=antecedentes,
        )
        return jsonify({"success": True, **resultado})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@diagnostics_bp.route("/api/diagnose/final", methods=["POST"])
@requires_login
def api_diagnose_final():
    blocked = _block_secretaria()
    if blocked:
        return blocked

    data              = request.json or {}
    patient_id        = data.get("patient_id")
    patient_name      = data.get("patient_name", "Paciente Anónimo")
    motivo_consulta   = data.get("motivo_consulta", "Sin especificar")
    motivo_emergencia = data.get("motivo_emergencia")
    visit_type        = data.get("visit_type", "consulta")
    visit_id          = data.get("visit_id")
    preliminar_probs  = data.get("preliminar_probs", {})
    tests_resultados  = data.get("tests_resultados", [])
    sintomas          = data.get("sintomas", {})
    antecedentes      = data.get("antecedentes", {})
    constantes        = data.get("constantes", {})

    try:
        probabilidades, pasos = engine.calcular_diagnostico_final(
            preliminar_probs, tests_resultados
        )

        diagnostico  = max(probabilidades, key=probabilidades.get)
        probabilidad = probabilidades[diagnostico]

        sintomas_activos     = [s for s, pres in sintomas.items() if pres]
        antecedentes_activos = [a for a, pres in antecedentes.items() if pres]

        meta = CLINICAL_METADATA.get(diagnostico, {})

        # ── Intentar generar sección fisiopatológica con Gemini ───────────────
        gemini_result = gemini_layer.generar_informe_clinico(
            paciente_nombre=patient_name,
            constantes=constantes,
            diagnostico=diagnostico,
            probabilidad=probabilidad,
            sintomas_activos=sintomas_activos,
            antecedentes_activos=antecedentes_activos,
            diagnosticos_diferenciales=probabilidades,
            motivo_consulta=motivo_consulta,
            tipo_visita=visit_type,
            meta_clinica=meta,
        )

        # ── Generar informe combinado: estructura Offline + sección Gemini ────
        seccion_gemini = gemini_result.get("seccion_gemini")
        gemini_fallback = gemini_result.get("fallback", True)

        explicacion = OfflineAIEngine.generar_explicacion(
            patient_name, constantes, diagnostico, probabilidad,
            sintomas_activos, antecedentes_activos, probabilidades,
            motivo_consulta, visit_type,
            seccion_gemini_override=seccion_gemini,
        )

        is_refuted = data.get("is_refuted", False)
        refutation_reason = data.get("refutation_reason")
        doctor_override_diagnosis = data.get("doctor_override_diagnosis")
        should_save = data.get("save_diagnosis", False)

        if visit_id and should_save:
            save_diagnosis(
                visit_id=int(visit_id),
                phase="final",
                diagnosis_primary=diagnostico,
                probability=probabilidad,
                alert_level=meta.get("alert_level", "Verde"),
                alert_color=meta.get("color", "#10b981"),
                specialist=meta.get("specialist", "Medicina General"),
                differentials=probabilidades,
                clinical_report=explicacion,
                is_refuted=is_refuted,
                refutation_reason=refutation_reason,
                doctor_override_diagnosis=doctor_override_diagnosis
            )
            if tests_resultados:
                save_visit_tests(int(visit_id), tests_resultados)

        return jsonify({
            "success": True,
            "patient_name": patient_name,
            "motivo_consulta": motivo_consulta,
            "visit_type": visit_type,
            "constantes": constantes,
            "probabilities": probabilidades,
            "diagnosis": diagnostico,
            "probability": probabilidad,
            "explanation": explicacion,
            "alert_level": meta.get("alert_level", "Verde"),
            "color": meta.get("color", "#10b981"),
            "specialist": meta.get("specialist", "Medicina General"),
            "pasos_calculo": pasos,
            "tests": tests_resultados,
            "gemini_used": not gemini_fallback,
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@diagnostics_bp.route("/api/diagnose/chat-gemini", methods=["POST"])
@requires_login
def api_diagnose_chat_gemini():
    """
    Chatbot médico con contexto bayesiano completo del paciente.
    Reemplaza el chatbot offline de palabras clave con Gemini.
    """
    blocked = _block_secretaria()
    if blocked:
        return blocked

    data         = request.json or {}
    diagnostico  = data.get("diagnostico", "")
    probabilidad = float(data.get("probabilidad", 0.0))
    sintomas     = data.get("sintomas_activos", [])
    antecedentes = data.get("antecedentes_activos", [])
    constantes   = data.get("constantes", {})
    mensaje      = data.get("message", "")
    historial    = data.get("history", [])

    if not mensaje:
        return jsonify({"success": False, "error": "Mensaje vacío."}), 400
    if not diagnostico:
        return jsonify({"success": False, "error": "Se requiere un diagnóstico activo."}), 400

    meta = CLINICAL_METADATA.get(diagnostico, {})

    try:
        result = gemini_layer.chatear_medico(
            diagnostico=diagnostico,
            probabilidad=probabilidad,
            sintomas_activos=sintomas,
            antecedentes_activos=antecedentes,
            constantes=constantes,
            mensaje_usuario=mensaje,
            historial=historial,
            meta_clinica=meta,
        )
        return jsonify({"success": True, **result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@diagnostics_bp.route("/api/clinical_metadata/<disease>", methods=["GET"])
@requires_login
def api_clinical_metadata(disease):
    blocked = _block_secretaria()
    if blocked:
        return blocked
    meta = CLINICAL_METADATA.get(disease)
    if not meta:
        return jsonify({"success": False, "error": "Enfermedad no encontrada."}), 404
    return jsonify({"success": True, "disease": disease, "metadata": meta})


@diagnostics_bp.route("/api/medical_tests", methods=["GET"])
@requires_login
def api_get_medical_tests():
    blocked = _block_secretaria()
    if blocked:
        return blocked
    return jsonify({"success": True, "tests": get_medical_tests()})
