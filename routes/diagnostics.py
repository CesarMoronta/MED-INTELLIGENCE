from flask import Blueprint, request, jsonify
from extensions import engine, gemini_layer
from database import save_diagnosis, save_visit_tests, get_medical_tests, get_user_by_id, log_audit_action
from diagnostic_engine import OfflineAIEngine, CLINICAL_METADATA
from utils import requires_login, get_current_user, get_client_ip

diagnostics_bp = Blueprint("diagnostics_bp", __name__)


def _block_secretaria():
    """Retorna 403 si el usuario actual es secretaria."""
    from utils import get_current_user
    u = get_current_user()
    if u.get("role") == "secretaria":
        return jsonify({"success": False, "error": "Permiso denegado."}), 403
    return None


def _check_subscription():
    """Retorna 403 si el doctor no tiene una suscripción activa."""
    u = get_current_user()
    if u.get("role") == "doctor":
        user_db = get_user_by_id(u["id"])
        if not user_db or not user_db.get("subscription_active"):
            return jsonify({
                "success": False,
                "error": "subscription_required",
                "message": "Se requiere una suscripción VIP activa de PayPal para usar el diagnóstico asistido por IA."
            }), 403
    return None


@diagnostics_bp.route("/api/diagnose/preliminar", methods=["POST"])
@requires_login
def api_diagnose_preliminar():
    blocked = _block_secretaria()
    if blocked:
        return blocked

    sub_blocked = _check_subscription()
    if sub_blocked:
        return sub_blocked

    data         = request.json or {}
    antecedentes = data.get("antecedentes", {})
    sintomas     = data.get("sintomas", {})
    constantes   = data.get("constantes", {})

    def safe_int(val, default):
        if val is None or val == "":
            return default
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return default

    def safe_float(val, default):
        if val is None or val == "":
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    edad        = safe_int(constantes.get("edad") or data.get("edad"), 30)
    temperatura = safe_float(constantes.get("temperatura") or data.get("temperatura"), 37.0)
    spo2        = safe_int(constantes.get("spo2") or data.get("spo2"), 98)
    pas         = safe_int(constantes.get("pas") or data.get("pas"), 120)
    pad         = safe_int(constantes.get("pad") or data.get("pad"), 80)
    fc          = safe_int(constantes.get("fc") or data.get("fc"), 80)
    fr          = safe_int(constantes.get("fr") or data.get("fr"), 16)

    # Validar rangos clínicos básicos para evitar cómputos insensatos
    edad        = max(0, min(edad, 125))
    temperatura = max(30.0, min(temperatura, 45.0))
    spo2        = max(0, min(spo2, 100))
    pas         = max(30, min(pas, 280))
    pad         = max(10, min(pad, 180))
    fc          = max(0, min(fc, 300))
    fr          = max(0, min(fr, 100))

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


@diagnostics_bp.route("/api/diagnose/extract-symptoms", methods=["POST"])
@requires_login
def api_extract_symptoms():
    blocked = _block_secretaria()
    if blocked:
        return blocked

    sub_blocked = _check_subscription()
    if sub_blocked:
        return sub_blocked

    data = request.json or {}
    narrative = data.get("narrative", "").strip()
    if not narrative:
        return jsonify({"success": False, "error": "Relato clínico vacío."}), 400

    try:
        sintomas_estandar = list(engine.P_sintoma.keys())
        sintomas_detectados = gemini_layer.extraer_sintomas_de_narrativa(narrative, sintomas_estandar)
        return jsonify({"success": True, "sintomas": sintomas_detectados})
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

    sub_blocked = _check_subscription()
    if sub_blocked:
        return sub_blocked

    data         = request.json or {}
    probs_bayes  = data.get("probabilities", {})
    sintomas     = data.get("sintomas", {})
    constantes   = data.get("constantes", {})
    antecedentes = data.get("antecedentes", {})
    motivo       = data.get("motivo_consulta") or data.get("motivo")
    tests_resultados = data.get("tests_resultados")

    if not probs_bayes:
        return jsonify({"success": False, "error": "Se requieren probabilidades bayesianas."}), 400

    try:
        resultado = gemini_layer.enriquecer_diagnostico_preliminar(
            probs_bayes=probs_bayes,
            sintomas=sintomas,
            constantes=constantes,
            antecedentes=antecedentes,
            motivo_consulta=motivo,
            tests_resultados=tests_resultados
        )
        return jsonify({"success": True, **resultado})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



@diagnostics_bp.route("/api/diagnose/phase2-calculate", methods=["POST"])
@requires_login
def api_diagnose_phase2_calculate():
    blocked = _block_secretaria()
    if blocked:
        return blocked

    data = request.json or {}
    preliminar_probs  = data.get("preliminar_probs", {})
    tests_resultados  = data.get("tests_resultados", [])

    try:
        probabilidades, pasos = engine.calcular_diagnostico_final(
            preliminar_probs, tests_resultados
        )
        return jsonify({
            "success": True,
            "probabilities": probabilidades,
            "pasos_calculo": pasos
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@diagnostics_bp.route("/api/diagnose/refinement-questions", methods=["POST"])
@requires_login
def api_diagnose_refinement_questions():
    blocked = _block_secretaria()
    if blocked:
        return blocked

    sub_blocked = _check_subscription()
    if sub_blocked:
        return sub_blocked

    data = request.json or {}
    probs_bayes = data.get("probabilities", {})
    sintomas = data.get("sintomas", {})
    constantes = data.get("constantes", {})
    antecedentes = data.get("antecedentes", {})

    if not probs_bayes:
        return jsonify({"success": False, "error": "Se requieren probabilidades bayesianas preliminares."}), 400

    try:
        sintomas_estandar = list(engine.P_sintoma.keys())
        sintomas_no_presentes = [s for s in sintomas_estandar if not sintomas.get(s, False)]

        resultado = gemini_layer.generar_preguntas_depuracion(
            probs_bayes=probs_bayes,
            sintomas=sintomas,
            constantes=constantes,
            antecedentes=antecedentes,
            sintomas_permitidos=sintomas_no_presentes
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
    constantes_raw    = data.get("constantes", {})

    def safe_int(val, default):
        if val is None or val == "":
            return default
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return default

    def safe_float(val, default):
        if val is None or val == "":
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    constantes = {
        "edad": safe_int(constantes_raw.get("edad"), 30),
        "temperatura": safe_float(constantes_raw.get("temperatura"), 37.0),
        "spo2": safe_int(constantes_raw.get("spo2"), 98),
        "pas": safe_int(constantes_raw.get("pas"), 120),
        "pad": safe_int(constantes_raw.get("pad"), 80),
        "fc": safe_int(constantes_raw.get("fc"), 80),
        "fr": safe_int(constantes_raw.get("fr"), 16)
    }

    try:
        # Verificar si tiene suscripción activa o si requiere modo manual
        u = get_current_user()
        user_db = get_user_by_id(u["id"]) if u.get("id") else None
        is_subscribed = user_db.get("subscription_active", False) if user_db else False

        is_manual = data.get("is_manual", False) or not is_subscribed

        if is_manual:
            diagnostico = data.get("diagnosis_primary") or "Diagnóstico Clínico"
            probabilidad = float(data.get("probability") or 1.0)
            alert_level = data.get("alert_level", "Verde")
            alert_colors = {'Verde': '#10b981', 'Amarillo': '#f59e0b', 'Rojo': '#ef4444'}
            alert_color = alert_colors.get(alert_level, '#10b981')
            specialist = data.get("specialist") or "Medicina General"
            explicacion = data.get("explanation") or data.get("doctor_notes") or "Diagnóstico y anotaciones ingresadas manualmente por el médico."
            should_save = data.get("save_diagnosis", False)

            if visit_id and should_save:
                save_diagnosis(
                    visit_id=int(visit_id),
                    phase="final",
                    diagnosis_primary=diagnostico,
                    probability=probabilidad,
                    alert_level=alert_level,
                    alert_color=alert_color,
                    specialist=specialist,
                    differentials={diagnostico: probabilidad},
                    clinical_report=explicacion,
                    is_refuted=False,
                    refutation_reason=None,
                    doctor_override_diagnosis=None
                )
                if tests_resultados:
                    save_visit_tests(int(visit_id), tests_resultados)

                u = get_current_user()
                log_audit_action(
                    username=u.get("username"), action="CREATE", entity="Diagnosis",
                    entity_id=str(visit_id),
                    details=f"Guardó diagnóstico {diagnostico} (Fase final - Manual) para la visita ID {visit_id}",
                    ip_address=get_client_ip(), user_id=u.get("id")
                )

            return jsonify({
                "success": True,
                "patient_name": patient_name,
                "motivo_consulta": motivo_consulta,
                "visit_type": visit_type,
                "constantes": constantes,
                "probabilities": {diagnostico: probabilidad},
                "diagnosis": diagnostico,
                "probability": probabilidad,
                "explanation": explicacion,
                "alert_level": alert_level,
                "color": alert_color,
                "specialist": specialist,
                "pasos_calculo": 0,
                "tests": tests_resultados,
                "gemini_used": False,
                "is_manual": True
            })

        probabilidades, pasos = engine.calcular_diagnostico_final(
            preliminar_probs, tests_resultados
        )

        diagnostico_top  = max(probabilidades, key=probabilidades.get)
        diagnostico = data.get("confirmed_diagnosis") or diagnostico_top
        probabilidad = probabilidades.get(diagnostico, probabilidades[diagnostico_top])

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

        if diagnostico != diagnostico_top:
            is_refuted = True
            doctor_override_diagnosis = diagnostico
            refutation_reason = data.get("refutation_reason") or "El médico seleccionó este diagnóstico alternativo tras los estudios de Fase 2."
        else:
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

            u = get_current_user()
            log_audit_action(
                username=u.get("username"), action="CREATE", entity="Diagnosis",
                entity_id=str(visit_id),
                details=f"Guardó diagnóstico {diagnostico} (Fase final - Algorítmico) para la visita ID {visit_id}",
                ip_address=get_client_ip(), user_id=u.get("id")
            )

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

    sub_blocked = _check_subscription()
    if sub_blocked:
        return sub_blocked

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
