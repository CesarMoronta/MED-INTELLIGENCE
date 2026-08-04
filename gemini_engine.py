"""
gemini_engine.py — Capa de IA Gemini para MED-INTELLIGENCE PRO

Complementa el motor bayesiano con razonamiento clínico avanzado en lenguaje natural.
"""

import os
import json
import time
import requests
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# ── CONFIGURACIÓN ────────────────────────────────────────────────────────────
_MODEL = "gemini-2.5-flash"

# System prompts optimizados (más cortos para ahorrar tokens)
_SYSTEM_EXTRACTOR = """Eres un asistente de triaje médico. Tu misión es extraer una lista de síntomas clínicos estándar a partir de la historia narrativa del paciente.
Asigna True solo si el síntoma se relata como presente, o False si no se menciona o se niega explícitamente."""

_SYSTEM_INTERNISTA = """Eres un médico internista especialista de nivel hospitalario terciario con experiencia en diagnóstico diferencial complejo.

Tu misión es enriquecer el análisis probabilístico bayesiano con razonamiento clínico de alto nivel. Para ello:

1. EVALÚA el perfil demográfico completo del paciente (edad, género, antecedentes, tipo de sangre) y su relevancia en los diagnósticos de sospecha.
2. ANALIZA los resultados de laboratorio con criterio experto: determina si son normales o patológicos, identifica valores críticos y razona cómo cada resultado impacta el diagnóstico diferencial.
3. RAZONA con fisiopatología: explica el mecanismo por el cual los síntomas y hallazgos se relacionan con el diagnóstico más probable.
4. EVALÚA los diagnósticos diferenciales bayesianos en orden de probabilidad y justifica clínicamente por qué el top diagnóstico es más probable que los demás.
5. SUGIERE un plan terapéutico de primera línea (no definitivo, solo orientativo) coherente con el diagnóstico y el perfil del paciente.
6. CATEGORIZA la urgencia del caso: Ambulatorio (puede esperar consulta programada), Urgente (requiere atención en horas), o Emergencia (requiere atención inmediata).
7. ADVIERTE siempre: 'Esta herramienta es de apoyo diagnóstico. El diagnóstico y tratamiento final es responsabilidad exclusiva del médico tratante.'

Sé preciso, usa terminología médica estándar, y fundamenta cada afirmación en datos clínicos."""

_SYSTEM_CHATBOT = """Eres el Médico Internista de Apoyo de MED-INTELLIGENCE PRO, con formación de especialista en Medicina Interna de hospital universitario de tercer nivel.

Responde en español con terminología médica precisa pero accesible para el médico tratante. Organiza tu respuesta con estructura clara. Puedes usar hasta 4-6 párrafos cuando el tema lo requiera.

Para cada consulta:
- Responde con fundamento clínico y cita mecanismos fisiopatológicos cuando sean relevantes
- Menciona señales de alarma (red flags) si aplican al caso
- Considera el contexto completo del paciente (edad, antecedentes, constantes)
- Siempre concluye con: '⚕️ Recordatorio: Este análisis es de apoyo clínico y no reemplaza el juicio del médico tratante ni la evaluación presencial del paciente.'"""

_SYSTEM_RECETAS = """Eres un asistente médico experto en farmacología clínica y prescripción terapéutica.

Genera una sugerencia de receta médica para el caso proporcionado siguiendo estas directrices:

1. SEGURIDAD CRÍTICA:
   - Si el triage es ROJO o hay emergencia, prescribe ÚNICAMENTE manejo sintomático de soporte seguro (ej. Paracetamol) y añade una nota de derivación urgente.
   - Revisa los antecedentes para detectar alergias o contraindicaciones.
   - Ajusta dosis por edad: pediátrico (<12 años) usa dosis/kg, geriátrico (>65 años) considera función renal/hepática.

2. SELECCIÓN TERAPÉUTICA:
   - Prescribe medicamentos de primera línea basados en guías clínicas actualizadas.
   - Especifica: nombre genérico y comercial, forma farmacéutica, dosis por toma, frecuencia, duración total y cantidad exacta de unidades.
   - Incluye indicaciones claras para el paciente en lenguaje sencillo.

3. ADVERTENCIA OBLIGATORIA en el campo 'notes' del primer medicamento:
   'Esta sugerencia de receta es generada por IA como apoyo clínico. El médico tratante debe revisar y validar cada medicamento antes de prescribir.'"""

# ── SCHEMAS PYDANTIC PARA STRUCTURED OUTPUTS ──────────────────────────────────

class SymptomExtraction(BaseModel):
    sintomas_presentes: List[str] = Field(
        description="Lista de los nombres exactos de los síntomas estándar que están presentes en la historia del paciente."
    )

class DiagnosticEnrichment(BaseModel):
    validacion: str = Field(description="Análisis clínico detallado de coherencia entre diagnóstico, síntomas, constantes vitales y resultados de laboratorio. Incluye razonamiento fisiopatológico y justificación del diagnóstico diferencial (3-5 oraciones).")
    sintomas_sugeridos: List[str] = Field(description="Hasta 5 síntomas o hallazgos clínicos adicionales a explorar para confirmar o descartar los diagnósticos diferenciales principales.")
    alertas_gemini: List[str] = Field(description="Hasta 4 señales de alarma clínicas (red flags), criterios de hospitalización o emergencias que el médico debe tener en cuenta.")
    confianza_gemini: str = Field(description="Valoración de confianza clínica (Alta/Media/Baja), justificación detallada y factores que aumentan o reducen la certeza diagnóstica.")
    plan_terapeutico_sugerido: Optional[str] = Field(None, description="Sugerencia breve de primera línea de manejo terapéutico coherente con el diagnóstico más probable y el perfil del paciente. No es una prescripción definitiva, es orientativo para el médico.")
    nivel_urgencia: str = Field(description="Categoría de urgencia del caso: 'Ambulatorio' (puede esperar cita programada), 'Urgente' (atención en menos de 24h) o 'Emergencia' (atención inmediata, activar protocolo de urgencias).")
    diagnostico_propuesto: Optional[str] = Field(None, description="Si consideras que el diagnóstico bayesiano principal es clínicamente incorrecto o improbable basado en el conjunto de datos clínicos, propón el nombre exacto de la enfermedad correcta de la lista permitida. Si el diagnóstico bayesiano es correcto, deja en null.")

class MedicationItem(BaseModel):
    medication: str = Field(description="Nombre y presentación del medicamento (ej. Paracetamol 500mg)")
    dosage: str = Field(description="Dosis por toma (ej. 1 tableta)")
    frequency: str = Field(description="Frecuencia (ej. Cada 8 horas)")
    duration_days: int = Field(description="Duración en días")
    quantity: int = Field(description="Cantidad total de unidades")
    notes: str = Field(description="Indicaciones para el paciente")

class PrescriptionResponse(BaseModel):
    medications: List[MedicationItem]

class RefinementQuestionItem(BaseModel):
    sintoma: str = Field(description="Nombre exacto del síntoma de la lista estándar que se desea explorar y que NO esté ya marcado como presente.")
    pregunta: str = Field(description="Pregunta en lenguaje sencillo y amigable para el paciente para evaluar el síntoma.")
    tipo: str = Field(description="Tipo de respuesta esperado. Usualmente 'boolean' (para Sí/No).")

class RefinementQuestionsResponse(BaseModel):
    preguntas: List[RefinementQuestionItem] = Field(description="Lista de hasta 4 preguntas clave para depurar el diagnóstico.")

ENFERMEDADES_PERMITIDAS = [
    "Gripe Común / Influenza", "Neumonía", "Bronquitis Aguda", "Crisis Asmática Aguda",
    "Exacerbación Aguda de EPOC", "Infarto Agudo de Miocardio (IAM)", "Insuficiencia Cardíaca Congestiva (ICC)",
    "Miocarditis", "Encefalitis", "Accidente Cerebrovascular (ACV)", "Migraña Severa", "Dengue No Grave (Clásico)",
    "Dengue Grave", "Fiebre Zika", "Fiebre Chikungunya", "Otitis Media Aguda", "Otitis Externa Aguda",
    "Sinusitis Aguda", "COVID-19", "COVID-19 Grave", "Faringoamigdalitis Viral", "Faringoamigdalitis Estreptocócica",
    "Tromboembolismo Pulmonar", "Diabetes Mellitus Tipo 2", "Gastroenteritis Aguda Viral",
    "Gastroenteritis Aguda Bacteriana", "Gastroenteritis Aguda Parasitaria", "Resfriado Común (Rinofaringitis)",
    "Cistitis Aguda (IVU Baja)", "Pielonefritis Aguda (IVU Alta)", "Reflujo Gastroesofágico (ERGE)",
    "Gastritis Aguda", "Úlcera Péptica No Complicada", "Varicela (Leve/Moderada)"
]



class GeminiDiagnosticLayer:
    """
    Capa de enriquecimiento clínico con IA Gemini.
    """

    def __init__(self):
        self.client = None
        self.available = False
        self.symptom_cache = {}
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                self.client = genai.Client(api_key=api_key)
                self.available = True
            except Exception as e:
                print(f"[GeminiLayer] Error inicializando cliente: {e}")

    def _generate_content_with_openrouter(self, contents, config, messages=None):
        """Intenta generar contenido mediante OpenRouter y retorna None si falla."""
        openrouter_key = os.environ.get("OPENROUTER_API_KEY")
        if not openrouter_key:
            return None

        openrouter_models = ["google/gemini-2.5-flash-lite", "google/gemini-2.5-flash", "openrouter/free"]

        if messages is None:
            prompt_text = ""
            if isinstance(contents, list):
                prompt_text = " ".join([str(c) for c in contents])
            else:
                prompt_text = str(contents)

            if config and hasattr(config, "response_schema") and config.response_schema:
                try:
                    schema_json = json.dumps(config.response_schema, default=lambda x: x.model_json_schema() if hasattr(x, "model_json_schema") else str(x))
                    prompt_text += f"\n\nResponde ÚNICAMENTE con un objeto JSON válido que cumpla este esquema:\n{schema_json}"
                except Exception:
                    pass
            elif config and hasattr(config, "response_mime_type") and config.response_mime_type == "application/json":
                prompt_text += "\n\nResponde ÚNICAMENTE con JSON válido."

            messages = [{"role": "user", "content": prompt_text}]
            if config and getattr(config, "system_instruction", None):
                messages.insert(0, {"role": "system", "content": str(config.system_instruction)})

        headers = {
            "Authorization": f"Bearer {openrouter_key}",
            "Content-Type": "application/json"
        }

        for or_model in openrouter_models:
            try:
                max_tokens = 2048
                if config and hasattr(config, "max_output_tokens") and config.max_output_tokens:
                    max_tokens = config.max_output_tokens

                payload = {
                    "model": or_model,
                    "messages": messages,
                    "max_tokens": max_tokens
                }
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                result_json = response.json()

                if "choices" in result_json and len(result_json["choices"]) > 0:
                    content_text = result_json["choices"][0]["message"]["content"]
                    print(f"[GeminiLayer] Fallback activado: usando OpenRouter ({or_model}) tras agotar pool de Gemini")

                    class OpenRouterResponse:
                        def __init__(self, text):
                            cleaned = text.strip()
                            if cleaned.startswith("```"):
                                lines = cleaned.splitlines()
                                if lines[0].startswith("```"):
                                    lines = lines[1:]
                                if lines and lines[-1].startswith("```"):
                                    lines = lines[:-1]
                                cleaned = "\n".join(lines).strip()
                            self.text = cleaned
                    return OpenRouterResponse(content_text)
            except Exception as e:
                print(f"[GeminiLayer] Error en OpenRouter con modelo {or_model}: {e}")

        return None

    def _generate_content_with_retry(self, contents, config) -> any:
        """
        Llama a la API de Gemini utilizando un pool de modelos alternativos y
        un mecanismo de reintentos con retroceso exponencial.
        """
        models_pool = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"]
        last_exception = None

        for model in models_pool:
            retries = 2
            backoff = 1.0
            for attempt in range(retries):
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=contents,
                        config=config,
                    )
                    return response
                except Exception as e:
                    last_exception = e
                    print(f"[GeminiLayer] Error con modelo {model} (intento {attempt+1}/{retries}): {e}")
                    if attempt < retries - 1:
                        time.sleep(backoff)
                        backoff *= 2.0
                    else:
                        break

        openrouter_response = self._generate_content_with_openrouter(contents, config)
        if openrouter_response is not None:
            return openrouter_response

        if last_exception is not None:
            raise last_exception
        raise Exception("Todos los modelos fallaron.")


    # ── NUEVA FUNCIÓN: EXTRACCIÓN DE SÍNTOMAS DESDE NARRATIVA ──────────────────
    def extraer_sintomas_de_narrativa(self, narrativa: str, lista_sintomas_estandar: list) -> dict:
        """
        Llama a Gemini para mapear la narrativa libre a la lista de síntomas booleanos estándar.
        """
        if not self.available or not narrativa:
            return {s: False for s in lista_sintomas_estandar}

        # Comprobar si la respuesta ya está en caché
        cache_key = narrativa.strip().lower()
        if cache_key in self.symptom_cache:
            print("[GeminiLayer] Retornando síntomas desde caché en memoria (0ms)")
            return self.symptom_cache[cache_key]

        sintomas_str = ", ".join(lista_sintomas_estandar)
        prompt = f"""Analiza la siguiente historia narrativa del paciente y determina cuáles de estos síntomas estándar están presentes:
SÍNTOMAS ESTÁNDAR PERMITIDOS:
{sintomas_str}

HISTORIA NARRATIVA:
"{narrativa}"

Devuelve la lista de síntomas que están presentes. Los nombres deben coincidir exactamente con alguno de los provistos en la lista de SÍNTOMAS ESTÁNDAR PERMITIDOS.
"""
        try:
            config = types.GenerateContentConfig(
                system_instruction=_SYSTEM_EXTRACTOR,
                temperature=0.1,
                max_output_tokens=1500,
                response_mime_type="application/json",
                response_schema=SymptomExtraction,
            )
            response = self._generate_content_with_retry(
                contents=prompt,
                config=config,
            )
            try:
                res = json.loads(response.text)
            except Exception as parse_err:
                print(f"[GeminiLayer] Falló parsing JSON de síntomas. Intentando recuperar texto directo: {parse_err}")
                res = {}
                # Intento de extracción simple si falla la estructura
                presentes = []
                for s in lista_sintomas_estandar:
                    if s.lower() in response.text.lower():
                        presentes.append(s)
                res["sintomas_presentes"] = presentes
            
            presentes = res.get("sintomas_presentes", [])
            
            # Convertir a diccionario de booleanos {sintoma: True/False}
            final_map = {}
            for s in lista_sintomas_estandar:
                val = False
                for p in presentes:
                    if p.strip().lower() == s.strip().lower():
                        val = True
                        break
                final_map[s] = val
            self.symptom_cache[cache_key] = final_map
            return final_map
        except Exception as e:
            print(f"[GeminiLayer] Error crítico en extracción de síntomas tras reintentos: {e}")
            return {s: False for s in lista_sintomas_estandar}

    # ── 1. ANÁLISIS ENRIQUECIDO POST-BAYES ────────────────────────────────────
    def enriquecer_diagnostico_preliminar(
        self,
        probs_bayes: dict,
        sintomas: dict,
        constantes: dict,
        antecedentes: dict,
        motivo_consulta: Optional[str] = None,
        tests_resultados: Optional[list] = None,
        patient_profile: Optional[dict] = None,
        tests_sugeridos: Optional[list] = None,
        doctor_notes: Optional[str] = None
    ) -> dict:
        if not self.available:
            return self._fallback_enriquecimiento(probs_bayes)

        # Top 5 diagnósticos bayesianos
        top5 = sorted(probs_bayes.items(), key=lambda x: x[1], reverse=True)[:5]
        top5_str = "\n".join([f"  {i+1}. {d}: {p*100:.2f}%" for i, (d, p) in enumerate(top5)])

        # AHORRO DE TOKENS: Filtrar para enviar solo activos
        sintomas_presentes  = [s for s, v in sintomas.items() if v]
        antecedentes_activos = [a for a, v in antecedentes.items() if v]

        # Perfil del Paciente
        profile_str = "PERFIL DEL PACIENTE:\n"
        if patient_profile:
            profile_str += f"  - Nombre: {patient_profile.get('name', 'Paciente Anónimo')}\n"
            profile_str += f"  - Edad: {patient_profile.get('age', constantes.get('edad', '30'))} años\n"
            profile_str += f"  - Género/Sexo: {patient_profile.get('gender', 'No especificado')}\n"
            profile_str += f"  - Tipo de Sangre: {patient_profile.get('blood_type', 'No especificado')}\n"
        else:
            profile_str += f"  - Edad: {constantes.get('edad', '30')} años\n"

        # Antecedentes Clínicos
        antecedentes_str = "ANTECEDENTES CLÍNICOS:\n"
        if antecedentes_activos:
            antecedentes_str += "\n".join([f"  - {a}" for a in antecedentes_activos]) + "\n"
        else:
            antecedentes_str += "  - Ninguno registrado\n"

        # Análisis Sugeridos
        sugeridos_str = ""
        if tests_sugeridos:
            sugeridos_str = "ANÁLISIS/ESTUDIOS CLÍNICOS SUGERIDOS INICIALMENTE:\n" + "\n".join([f"  - {t}" for t in tests_sugeridos]) + "\n"

        # Resultados de Análisis Clínicos Realizados
        tests_str = ""
        if tests_resultados:
            realized_tests = [f"{t['test_name']}: {t['result']}" for t in tests_resultados if t.get('done') and t.get('result')]
            if realized_tests:
                tests_str = "RESULTADOS DE ESTUDIOS/ANÁLISIS CLÍNICOS REALIZADOS CON SUS VALORES:\n" + "\n".join([f"  - {t}" for t in realized_tests]) + "\n"

        prompt = f"""El motor bayesiano procesó los datos y obtuvo:
TOP 5 DIAGNÓSTICOS BAYESIANOS:
{top5_str}

{profile_str}
SÍNTOMAS PRESENTES: {', '.join(sintomas_presentes) if sintomas_presentes else 'Ninguno'}
{antecedentes_str}
CONSTANTES VITALES: Temp {constantes.get('temperatura','?')}°C | SpO2 {constantes.get('spo2','?')}% | PA {constantes.get('pas','?')}/{constantes.get('pad','?')} | FC {constantes.get('fc','?')} | FR {constantes.get('fr','?')}
{sugeridos_str}
{tests_str}
"""
        if motivo_consulta:
            prompt += f'MOTIVO DE CONSULTA / HISTORIA DEL PACIENTE:\n"{motivo_consulta}"\n'

        if doctor_notes:
            prompt += f'NOTAS CLÍNICAS DEL MÉDICO TRATANTE:\n"{doctor_notes}"\n'

        prompt += f"""
[INSTRUCCIÓN CLÍNICA DETALLADA]:
Como médico internista de nivel hospitalario terciario, realiza una valoración clínica integral del caso:

1. PERFIL Y CONTEXTO: Evalúa la edad, género y antecedentes del paciente en relación con los diagnósticos de sospecha. Identifica factores de riesgo relevantes.

2. ANÁLISIS DE LABORATORIO (si aplica): Para cada resultado de prueba suministrado:
   - Determina si el valor es normal, alterado o crítico
   - Explica el significado clínico del hallazgo
   - Señala cómo impacta en la probabilidad de los diagnósticos diferenciales

3. RAZONAMIENTO FISIOPATOLÓGICO: Explica el mecanismo fisiopatológico que conecta los síntomas y hallazgos con el diagnóstico más probable.

4. DIFERENCIAL RAZONADO: Justifica por qué el diagnóstico top es más probable que los demás, y qué argumento clínico descarta cada alternativa.

5. PLAN TERAPÉUTICO (orientativo): Sugiere manejo de primera línea (no es prescripción definitiva).

6. URGENCIA: Categoriza el caso como 'Ambulatorio', 'Urgente' o 'Emergencia' según las constantes vitales, síntomas y diagnóstico probable.

[REGLA CLÍNICA DE DISCREPANCIA]:
Si consideras que el diagnóstico bayesiano #1 ({top5[0][0] if top5 else ''}) es clínicamente INCORRECTO o poco probable dada la totalidad del caso clínico, debes proponer el nombre exacto del diagnóstico correcto en 'diagnostico_propuesto' seleccionando de esta lista:
{", ".join(ENFERMEDADES_PERMITIDAS)}

Si el diagnóstico bayesiano es correcto, deja 'diagnostico_propuesto' como null.
"""

        try:
            config = types.GenerateContentConfig(
                system_instruction=_SYSTEM_INTERNISTA,
                temperature=0.3,
                max_output_tokens=2000,
                response_mime_type="application/json",
                response_schema=DiagnosticEnrichment,
            )
            response = self._generate_content_with_retry(
                contents=prompt,
                config=config,
            )
            try:
                result = json.loads(response.text)
            except Exception as parse_err:
                print(f"[GeminiLayer] Error parseando enriquecimiento: {parse_err}. Generando fallback seguro.")
                result = self._fallback_enriquecimiento(probs_bayes)
                result["fallback"] = False
                return result

            result["fallback"] = False
            return result
        except Exception as e:
            print(f"[GeminiLayer] Error crítico en enriquecimiento tras reintentos: {e}")
            return self._fallback_enriquecimiento(probs_bayes)

    def _fallback_enriquecimiento(self, probs_bayes: dict) -> dict:
        top = max(probs_bayes, key=probs_bayes.get)
        return {
            "validacion": f"Análisis bayesiano completado. El diagnóstico más probable es {top}. Considere el contexto clínico completo antes de concluir. Esta herramienta es de apoyo, no reemplaza el juicio del médico tratante.",
            "sintomas_sugeridos": [],
            "alertas_gemini": [],
            "confianza_gemini": "No disponible (modo offline)",
            "plan_terapeutico_sugerido": None,
            "nivel_urgencia": "Ambulatorio",
            "fallback": True,
        }

    # ── 2. INFORME CLÍNICO ENRIQUECIDO ────────────────────────────────────────
    def generar_informe_clinico(
        self,
        paciente_nombre: str,
        constantes: dict,
        diagnostico: str,
        probabilidad: float,
        sintomas_activos: list,
        antecedentes_activos: list,
        diagnosticos_diferenciales: dict,
        motivo_consulta: str = "No especificado",
        tipo_visita: str = "consulta",
        meta_clinica: dict = None,
        doctor_notes: str = "",
        tests_resultados: list = None,
        blood_type: str = None,
    ) -> dict:
        if not self.available:
            return {"informe_completo": None, "seccion_gemini": None, "fallback": True}

        meta = meta_clinica or {}
        top5 = sorted(diagnosticos_diferenciales.items(), key=lambda x: x[1], reverse=True)[:5]
        diferenciales_str = "\n".join([f"  {i+1}. {d}: {p*100:.2f}%" for i, (d, p) in enumerate(top5)])

        alert_level = meta.get("alert_level", "Verde")
        emoji_nivel = {"Rojo": "🔴", "Amarillo": "🟡", "Verde": "🟢"}.get(alert_level, "🟢")
        specialist = meta.get("specialist", "Medicina General")

        # Preparar resultados de laboratorio
        labs_str = ""
        if tests_resultados:
            labs = [f"  - {t['test_name']}: {t['result']}" for t in tests_resultados if t.get('done') and t.get('result')]
            if labs:
                labs_str = "RESULTADOS DE LABORATORIO Y ESTUDIOS CLÍNICOS:\n" + "\n".join(labs) + "\n"

        prompt = f"""Genera un INFORME CLÍNICO MÉDICO COMPLETO en markdown para el siguiente caso clínico.

=== DATOS DEL CASO CLÍNICO ===
PACIENTE: {paciente_nombre}
TIPO VISITA: {tipo_visita.upper()} | TRIAGE: {alert_level} {emoji_nivel}
DIAGNÓSTICO: {diagnostico} (confianza bayesiana: {probabilidad*100:.2f}%)
ESPECIALISTA SUGERIDO: {specialist}
MOTIVO DE CONSULTA: {motivo_consulta}

CONSTANTES VITALES:
  - Temperatura: {constantes.get('temperatura','?')}°C
  - SpO2: {constantes.get('spo2','?')}%
  - PA: {constantes.get('pas','?')}/{constantes.get('pad','?')} mmHg
  - FC: {constantes.get('fc','?')} bpm | FR: {constantes.get('fr','?')} rpm
  - IMC: {constantes.get('imc','No registrado')} | Tipo de Sangre: {blood_type or 'No registrado'}

SÍNTOMAS PRESENTES: {', '.join(sintomas_activos) if sintomas_activos else 'Ninguno reportado'}
ANTECEDENTES PATOLÓGICOS: {', '.join(antecedentes_activos) if antecedentes_activos else 'Ninguno reportado'}

DIAGNÓSTICOS DIFERENCIALES (probabilidades bayesianas):
{diferenciales_str}

{labs_str}
{f'NOTAS DEL MÉDICO TRATANTE: {doctor_notes}' if doctor_notes else ''}

=== INSTRUCCIÓN PARA EL INFORME ===
Genera un informe clínico médico completo, profesional y estructurado en formato markdown con las siguientes secciones:

## 📋 Presentación Clínica
Resumen conciso del cuadro clínico actual (síntomas, tiempo de evolución inferido, contexto).

## 🔬 Hallazgos Relevantes
Hallazgos objetivos (constantes vitales, valores de laboratorio si aplica). Para cada valor alterado, indica su relevancia clínica.

## 🧬 Análisis Fisiopatológico
Explica el mecanismo fisiopatológico que conecta los síntomas, hallazgos y antecedentes con el diagnóstico.

## ⚖️ Diagnóstico Diferencial Razonado
Justifica por qué se establece el diagnóstico principal sobre los demás diferenciales. Menciona qué argumenta en contra de cada alternativa.

## 💊 Plan Terapéutico Sugerido (Orientativo)
Primera línea de manejo sugerida (no es prescripción definitiva): medidas generales, tratamiento farmacológico de primera línea según guías, estudios complementarios recomendados.

## ⚠️ Señales de Alarma
Lista de signos y síntomas que deben alertar al médico para hospitalización, cambio de tratamiento o activación de protocolo de urgencias.

## 📌 Recomendaciones al Paciente
Indicaciones claras y prácticas en lenguaje sencillo para el paciente sobre cuidados en casa, dieta, actividad física y cuándo acudir a urgencias.

---
> ⚕️ **Aviso Clínico Importante**: Este informe es generado por inteligencia artificial como herramienta de apoyo diagnóstico. **No constituye un diagnóstico médico definitivo** y no reemplaza el juicio clínico del médico tratante. El diagnóstico y tratamiento final es responsabilidad exclusiva del profesional de salud que atiende al paciente.
"""

        try:
            config = types.GenerateContentConfig(
                system_instruction=_SYSTEM_INTERNISTA,
                temperature=0.35,
                max_output_tokens=2500,
            )
            response = self._generate_content_with_retry(
                contents=prompt,
                config=config,
            )
            seccion_gemini = response.text.strip()
            return {
                "seccion_gemini": seccion_gemini,
                "fallback": False,
            }
        except Exception as e:
            print(f"[GeminiLayer] Error crítico generando informe tras reintentos: {e}")
            return {"seccion_gemini": None, "fallback": True}


    # ── 3. CHATBOT MÉDICO CON CONTEXTO BAYESIANO ──────────────────────────────
    def chatear_medico(
        self,
        diagnostico: str,
        probabilidad: float,
        sintomas_activos: list,
        antecedentes_activos: list,
        constantes: dict,
        mensaje_usuario: str,
        historial: list,
        meta_clinica: dict = None,
    ) -> dict:
        if not self.available:
            return {"response": self._fallback_chat(diagnostico, mensaje_usuario), "fallback": True}

        meta = meta_clinica or {}
        alert_level = meta.get("alert_level", "Verde")

        system_con_contexto = f"""{_SYSTEM_CHATBOT}

=== CONTEXTO DEL PACIENTE ===
Diagnóstico: {diagnostico} ({probabilidad*100:.2f}%)
Triage: {alert_level}
Síntomas: {', '.join(sintomas_activos)}
Antecedentes: {', '.join(antecedentes_activos)}
Constantes: Temp {constantes.get('temperatura')}°C | SpO2 {constantes.get('spo2')}% | PA {constantes.get('pas')}/{constantes.get('pad')} | FC {constantes.get('fc')}
=== FIN CONTEXTO ==="""

        try:
            formatted_history = []
            for msg in historial:
                formatted_history.append(
                    types.Content(
                        role=msg.get("role", "user"),
                        parts=[types.Part.from_text(text=msg.get("text", ""))]
                    )
                )

            models_pool = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-pro"]
            last_exception = None

            for model in models_pool:
                retries = 3
                backoff = 1.5
                for attempt in range(retries):
                    try:
                        chat = self.client.chats.create(
                            model=model,
                            config=types.GenerateContentConfig(
                                system_instruction=system_con_contexto,
                                temperature=0.5,
                                max_output_tokens=1000,
                            ),
                        )
                        if formatted_history:
                            chat._history = formatted_history

                        response = chat.send_message(mensaje_usuario)
                        return {"response": response.text, "fallback": False}
                    except Exception as e:
                        last_exception = e
                        print(f"[GeminiLayer] Error en chat médico con modelo {model} (intento {attempt+1}/{retries}): {e}")
                        if attempt < retries - 1:
                            time.sleep(backoff)
                            backoff *= 2.0
                        else:
                            break

            openrouter_messages = [{"role": "system", "content": system_con_contexto}]
            for msg in historial:
                role = msg.get("role", "user")
                if role == "model":
                    role = "assistant"
                if role not in ("user", "assistant"):
                    role = "user"
                openrouter_messages.append({"role": role, "content": msg.get("text", "")})
            openrouter_messages.append({"role": "user", "content": mensaje_usuario})

            config = types.GenerateContentConfig(
                system_instruction=system_con_contexto,
                temperature=0.5,
                max_output_tokens=1000,
            )
            openrouter_response = self._generate_content_with_openrouter(
                contents=mensaje_usuario,
                config=config,
                messages=openrouter_messages,
            )
            if openrouter_response is not None:
                return {"response": openrouter_response.text, "fallback": False}

            if last_exception is not None:
                raise last_exception
            raise Exception("Todos los modelos de chat fallaron.")
        except Exception as e:
            print(f"[GeminiLayer] Error crítico en chat médico tras reintentos y fallback: {e}")
            return {"response": self._fallback_chat(diagnostico, mensaje_usuario), "fallback": True}

    def _fallback_chat(self, diagnostico: str, mensaje: str) -> str:
        return f"El asistente médico IA no está disponible en este momento. Consulte el informe clínico para **{diagnostico}**."

    # ── 4. SUGERENCIA DE RECETA MÉDICA CON GUARDRAILS ─────────────────────────
    def generar_receta_con_ia(
        self,
        diagnostico: str,
        motivo_consulta: str,
        doctor_notes: str,
        constantes: dict,
        sintomas_activos: list,
        antecedentes_activos: list,
        paciente_edad: int,
        paciente_genero: str,
        alert_level: str,
        blood_type: str = None,
        tests_resultados: list = None
    ) -> dict:
        if not self.available:
            return {"medications": [], "fallback": True}

        # GUARDRAIL EN PYTHON: Si el triage es crítico, forzar receta de alivio sintomático básico
        es_critico = alert_level.strip().lower() in ["rojo", "crítico", "critico"]

        # Grupo de edad para ajuste farmacológico
        grupo_edad = "pediátrico (<12 años)" if paciente_edad < 12 else ("geriátrico (>65 años)" if paciente_edad > 65 else "adulto")

        # Preparar resultados de laboratorio relevantes
        labs_str = ""
        if tests_resultados:
            labs = [f"  - {t['test_name']}: {t['result']}" for t in tests_resultados if t.get('done') and t.get('result')]
            if labs:
                labs_str = "RESULTADOS DE LABORATORIO DISPONIBLES:\n" + "\n".join(labs)

        prompt = f"""Genera una sugerencia de receta médica fundamentada para el siguiente caso clínico:

PERFIL DEL PACIENTE:
  - Edad: {paciente_edad} años ({grupo_edad})
  - Género: {paciente_genero}
  - Tipo de Sangre: {blood_type or 'No registrado'}

DIAGNÓSTICO: {diagnostico}
NIVEL DE TRIAGE: {alert_level}
MOTIVO DE CONSULTA: {motivo_consulta}

CONSTANTES VITALES:
  - Temperatura: {constantes.get('temperatura','?')}°C | SpO2: {constantes.get('spo2','?')}%
  - PA: {constantes.get('pas','?')}/{constantes.get('pad','?')} mmHg | FC: {constantes.get('fc','?')} bpm
  - IMC: {constantes.get('imc', 'No registrado')}

SÍNTOMAS ACTIVOS: {', '.join(sintomas_activos) if sintomas_activos else 'Ninguno'}
ANTECEDENTES PATOLÓGICOS: {', '.join(antecedentes_activos) if antecedentes_activos else 'Ninguno'}
{labs_str}
NOTAS DEL MÉDICO TRATANTE: {doctor_notes or 'Sin notas adicionales'}
"""
        if es_critico:
            prompt += "\n[GUARDRAIL CRÍTICO]: El triage es ROJO. Prescribe ÚNICAMENTE analgésico/antipirético simple de soporte. En el campo 'notes' del primer medicamento incluye: 'URGENTE: Derivar a urgencias hospitalarias de forma inmediata.'"
        if paciente_edad < 12:
            prompt += "\n[AJUSTE PEDIÁTRICO]: Paciente menor de 12 años. Calcula dosis según peso/kg. Evita medicamentos contraindicados en pediatría (AINEs en <2 años, quinolonas, etc.)."
        elif paciente_edad > 65:
            prompt += "\n[AJUSTE GERIÁTRICO]: Paciente mayor de 65 años. Ajusta dosis considerando función renal/hepática reducida. Evita polifarmacia y medicamentos con alto riesgo en ancianos (benzodiacepinas, anticolinérgicos fuertes)."

        try:
            config = types.GenerateContentConfig(
                system_instruction=_SYSTEM_RECETAS,
                temperature=0.2,
                max_output_tokens=1500,
                response_mime_type="application/json",
                response_schema=PrescriptionResponse,
            )
            response = self._generate_content_with_retry(
                contents=prompt,
                config=config,
            )
            
            try:
                result = json.loads(response.text)
            except Exception as parse_err:
                print(f"[GeminiLayer] Falló el parsing JSON de la receta: {parse_err}")
                # Fallback simple seguro: recetar Paracetamol
                result = {
                    "medications": [
                        {
                            "medication": "Paracetamol 500mg",
                            "dosage": "1 tableta",
                            "frequency": "Cada 8 horas",
                            "duration_days": 3,
                            "quantity": 10,
                            "notes": "Tomar en caso de dolor o fiebre. Se usó el modo de contingencia clínica."
                        }
                    ]
                }
            
            # GUARDRAIL EXTRA: Validar alergias registradas del paciente a nivel de código
            tiene_alergia_penicilina = any(
                "penicilina" in ant.lower() or "alergia" in ant.lower()
                for ant in antecedentes_activos
            )
            if tiene_alergia_penicilina:
                # Remover cualquier betalactámico o penicilina sugerido por error
                antibioticos_peligrosos = ["amoxicilina", "penicilina", "ampicilina", "piperacilina", "clavulan"]
                filtered_meds = []
                for med in result.get("medications", []):
                    med_name = med.get("medication", "").lower()
                    if any(ap in med_name for ap in antibioticos_peligrosos):
                        # Reemplazar por una nota o sustituto seguro
                        med["medication"] = "Sustituto no penicilínico (Ej. Claritromicina 500mg)"
                        med["notes"] = "⚠️ AJUSTADO: Se detectó antecedente de alergia a la penicilina."
                    filtered_meds.append(med)
                result["medications"] = filtered_meds

            result["fallback"] = False
            return result
        except Exception as e:
            print(f"[GeminiLayer] Error crítico generando receta tras reintentos: {e}")
            return {"medications": [], "fallback": True}

    def generar_preguntas_depuracion(
        self,
        probs_bayes: dict,
        sintomas: dict,
        constantes: dict,
        antecedentes: dict,
        sintomas_permitidos: List[str]
    ) -> dict:
        if not self.available:
            return {"preguntas": []}

        top3 = sorted(probs_bayes.items(), key=lambda x: x[1], reverse=True)[:3]
        top3_str = "\n".join([f"  - {d}: {p*100:.2f}%" for d, p in top3])

        sintomas_presentes = [s for s, v in sintomas.items() if v]
        antecedentes_activos = [a for a, v in antecedentes.items() if v]

        prompt = f"""Eres un médico internista realizando diagnóstico diferencial interactivo. 
A partir de:
- Diagnósticos probables (Bayes):
{top3_str}
- Síntomas ya presentes: {', '.join(sintomas_presentes) if sintomas_presentes else 'Ninguno'}
- Antecedentes clínicos: {', '.join(antecedentes_activos) if antecedentes_activos else 'Ninguno'}
- Constantes vitales: Temp {constantes.get('temperatura','?')}°C | SpO2 {constantes.get('spo2','?')}% | FC {constantes.get('fc','?')} | FR {constantes.get('fr','?')}

Tu objetivo es formular hasta 4 preguntas clave para el paciente. 
Cada pregunta debe evaluar la presencia o ausencia de un síntoma de la siguiente lista de síntomas estándares (debes elegir únicamente de esta lista de síntomas estándar y que NO estén ya presentes):
{", ".join(sintomas_permitidos)}

Estas preguntas deben estar diseñadas estratégicamente para confirmar el diagnóstico sospechado o descartar los diferenciales inmediatos (por ejemplo, diferenciar entre faringoamigdalitis viral y estreptocócica, o entre dengue y zika/chikungunya, o entre cistitis y pielonefritis).
Devuelve el JSON correspondiente.
"""
        try:
            config = types.GenerateContentConfig(
                system_instruction="Eres un médico experto optimizando el triaje diagnóstico.",
                temperature=0.2,
                max_output_tokens=1000,
                response_mime_type="application/json",
                response_schema=RefinementQuestionsResponse,
            )
            response = self._generate_content_with_retry(
                contents=prompt,
                config=config,
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[GeminiLayer] Error en generar_preguntas_depuracion: {e}")
            return {"preguntas": []}

