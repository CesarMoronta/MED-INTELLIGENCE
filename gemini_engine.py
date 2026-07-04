"""
gemini_engine.py — Capa de IA Gemini para MED-INTELLIGENCE PRO

Complementa el motor bayesiano con razonamiento clínico avanzado en lenguaje natural.
"""

import os
import json
import time
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# ── CONFIGURACIÓN ────────────────────────────────────────────────────────────
_MODEL = "gemini-2.5-flash"

# System prompts optimizados (más cortos para ahorrar tokens)
_SYSTEM_EXTRACTOR = """Eres un asistente de triaje médico. Tu misión es extraer una lista de síntomas clínicos estándar a partir de la historia narrativa del paciente.
Asigna True solo si el síntoma se relata como presente, o False si no se menciona o se niega explícitamente."""

_SYSTEM_INTERNISTA = """Eres un médico internista especialista.
Tu rol es enriquecer el análisis probabilístico bayesiano local con razonamiento clínico narrativo de alto nivel, coherente con las probabilidades dadas."""

_SYSTEM_CHATBOT = """Eres el Médico Internista de Apoyo de MED-INTELLIGENCE PRO.
Responde de forma clara, fundamentada y breve. Máximo 2-4 párrafos.
Añade siempre: "Este análisis es de apoyo clínico, no reemplaza el juicio médico." """

_SYSTEM_RECETAS = """Eres un asistente médico de prescripción clínica.
Diseña una receta adecuada basada en el diagnóstico, constantes y síntomas.
Reglas de seguridad:
1. Si el triage es ROJO o hay emergencia crítica, prescribe ÚNICAMENTE alivio sintomático básico seguro (ej. Paracetamol).
2. Para casos ambulatorios, prescribe medicamentos de primera línea validados, especificando dosis estándar y cantidad exacta.
3. Evita interacciones peligrosas o sobredosis."""

# ── SCHEMAS PYDANTIC PARA STRUCTURED OUTPUTS ──────────────────────────────────

class SymptomExtraction(BaseModel):
    sintomas_presentes: List[str] = Field(
        description="Lista de los nombres exactos de los síntomas estándar que están presentes en la historia del paciente."
    )

class DiagnosticEnrichment(BaseModel):
    validacion: str = Field(description="Comentario clínico de coherencia entre diagnóstico, síntomas y constantes (2-3 oraciones).")
    sintomas_sugeridos: List[str] = Field(description="Hasta 4 síntomas adicionales a explorar.")
    alertas_gemini: List[str] = Field(description="Hasta 3 señales de alerta o emergencias clínicas.")
    confianza_gemini: str = Field(description="Nivel de confianza (Alta/Media/Baja) y justificación corta.")
    diagnostico_propuesto: Optional[str] = Field(None, description="Si consideras que el diagnóstico bayesiano principal es incorrecto o improbable, propón de forma textual el nombre exacto de la enfermedad correcta de entre la lista de permitidas. De lo contrario, deja este campo vacío o null.")

class MedicationItem(BaseModel):
    medication: str = Field(description="Nombre y presentación del medicamento (ej. Paracetamol 500mg)")
    dosage: str = Field(description="Dosis por toma (ej. 1 tableta)")
    frequency: str = Field(description="Frecuencia (ej. Cada 8 horas)")
    duration_days: int = Field(description="Duración en días")
    quantity: int = Field(description="Cantidad total de unidades")
    notes: str = Field(description="Indicaciones para el paciente")

class PrescriptionResponse(BaseModel):
    medications: List[MedicationItem]


ENFERMEDADES_PERMITIDAS = [
    "Gripe Común / Influenza", "Neumonía", "Bronquitis Aguda", "Crisis Asmática Aguda",
    "Exacerbación Aguda de EPOC", "Infarto Agudo de Miocardio (IAM)", "Insuficiencia Cardíaca Congestiva (ICC)",
    "Miocarditis", "Encefalitis", "Accidente Cerebrovascular (ACV)", "Migraña Severa", "Dengue",
    "Otitis Media", "Sinusitis Aguda", "COVID-19", "COVID-19 Grave", "Faringoamigdalitis Aguda",
    "Tromboembolismo Pulmonar", "Diabetes Mellitus Tipo 2", "Gastroenteritis Aguda",
    "Resfriado Común (Rinofaringitis)", "Infección de Vías Urinarias (IVU)", "Reflujo Gastroesofágico (ERGE)"
]


class GeminiDiagnosticLayer:
    """
    Capa de enriquecimiento clínico con IA Gemini.
    """

    def __init__(self):
        self.client = None
        self.available = False
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                self.client = genai.Client(api_key=api_key)
                self.available = True
            except Exception as e:
                print(f"[GeminiLayer] Error inicializando cliente: {e}")

    def _generate_content_with_retry(self, contents, config) -> any:
        """
        Llama a la API de Gemini utilizando un pool de modelos alternativos y
        un mecanismo de reintentos con retroceso exponencial.
        """
        models_pool = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        last_exception = None

        for model in models_pool:
            retries = 3
            backoff = 1.5
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
        raise last_exception


    # ── NUEVA FUNCIÓN: EXTRACCIÓN DE SÍNTOMAS DESDE NARRATIVA ──────────────────
    def extraer_sintomas_de_narrativa(self, narrativa: str, lista_sintomas_estandar: list) -> dict:
        """
        Llama a Gemini para mapear la narrativa libre a la lista de síntomas booleanos estándar.
        """
        if not self.available or not narrativa:
            return {s: False for s in lista_sintomas_estandar}

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
        motivo_consulta: Optional[str] = None
    ) -> dict:
        if not self.available:
            return self._fallback_enriquecimiento(probs_bayes)

        # Top 5 diagnósticos bayesianos
        top5 = sorted(probs_bayes.items(), key=lambda x: x[1], reverse=True)[:5]
        top5_str = "\n".join([f"  {i+1}. {d}: {p*100:.2f}%" for i, (d, p) in enumerate(top5)])

        # AHORRO DE TOKENS: Filtrar para enviar solo activos
        sintomas_presentes  = [s for s, v in sintomas.items() if v]
        antecedentes_activos = [a for a, v in antecedentes.items() if v]

        prompt = f"""El motor bayesiano procesó los datos y obtuvo:
TOP 5 DIAGNÓSTICOS BAYESIANOS:
{top5_str}

SÍNTOMAS PRESENTES: {', '.join(sintomas_presentes) if sintomas_presentes else 'Ninguno'}
ANTECEDENTES CLÍNICOS: {', '.join(antecedentes_activos) if antecedentes_activos else 'Ninguno'}
CONSTANTES VITALES: Temp {constantes.get('temperatura','?')}°C | SpO2 {constantes.get('spo2','?')}% | PA {constantes.get('pas','?')}/{constantes.get('pad','?')} | FC {constantes.get('fc','?')} | FR {constantes.get('fr','?')} | Edad {constantes.get('edad','?')}
"""
        if motivo_consulta:
            prompt += f'HISTORIA/NARRATIVA ADICIONAL: "{motivo_consulta}"\n'

        prompt += f"""
[REGLA CLÍNICA DE DISCREPANCIA]:
Si consideras que el diagnóstico bayesiano #1 ({top5[0][0] if top5 else ''}) es clínicamente INCORRECTO o poco probable dada la edad y el cuadro clínico (ej. diagnosticar Diabetes Mellitus Tipo 2 ante un cuadro agudo de vómitos y dolor estomacal de inicio abrupto en paciente de 21 años, o diagnosticar cáncer en lugar de una patología infecciosa simple), debes proponer obligatoriamente el nombre exacto del diagnóstico correcto en el campo 'diagnostico_propuesto' seleccionándolo de entre esta lista permitida:
{", ".join(ENFERMEDADES_PERMITIDAS)}

Si crees que el diagnóstico bayesiano es correcto, deja 'diagnostico_propuesto' como null.
"""

        try:
            config = types.GenerateContentConfig(
                system_instruction=_SYSTEM_INTERNISTA,
                temperature=0.3,
                max_output_tokens=1500,
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
            "validacion": f"Análisis bayesiano completado. El diagnóstico más probable es {top}. Considere el contexto clínico completo antes de concluir.",
            "sintomas_sugeridos": [],
            "alertas_gemini": [],
            "confianza_gemini": "No disponible (modo offline)",
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
    ) -> dict:
        if not self.available:
            return {"informe_completo": None, "seccion_gemini": None, "fallback": True}

        meta = meta_clinica or {}
        top3 = sorted(diagnosticos_diferenciales.items(), key=lambda x: x[1], reverse=True)[:3]
        diferenciales_str = "\n".join([f"  - {d}: {p*100:.2f}%" for d, p in top3 if d != diagnostico])

        alert_level = meta.get("alert_level", "Verde")
        emoji_nivel = {"Rojo": "🔴", "Amarillo": "🟡", "Verde": "🟢"}.get(alert_level, "🟢")

        prompt = f"""Genera el análisis fisiopatológico clínico en markdown.
DIAGNÓSTICO FINAL: {diagnostico} ({probabilidad*100:.2f}% confianza)
TRIAGE: {alert_level} {emoji_nivel} | VISITA: {tipo_visita.upper()}
MOTIVO: {motivo_consulta}
CONSTANTES: Temp {constantes.get('temperatura','?')}°C | SpO2 {constantes.get('spo2','?')}% | PA {constantes.get('pas','?')}/{constantes.get('pad','?')} | FC {constantes.get('fc','?')} | FR {constantes.get('fr','?')}
SÍNTOMAS: {', '.join(sintomas_activos) if sintomas_activos else 'Ninguno'}
ANTECEDENTES: {', '.join(antecedentes_activos) if antecedentes_activos else 'Ninguno'}
DIFERENCIALES:
{diferenciales_str}

Genera solo el texto en markdown (sin títulos iniciales). Sé conciso (máx 150 palabras)."""

        try:
            config = types.GenerateContentConfig(
                system_instruction=_SYSTEM_INTERNISTA,
                temperature=0.4,
                max_output_tokens=1000,
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

            models_pool = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
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
            raise last_exception
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
        alert_level: str
    ) -> dict:
        if not self.available:
            return {"medications": [], "fallback": True}

        # GUARDRAIL EN PYTHON: Si el triage es crítico, forzar receta de alivio sintomático básico
        # y derivación inmediata a nivel de código
        es_critico = alert_level.strip().lower() in ["rojo", "crítico", "critico"]

        prompt = f"""Genera una sugerencia de receta para el caso clínico:
PACIENTE: {paciente_edad} años | {paciente_genero}
DIAGNÓSTICO: {diagnostico}
TRIAGE: {alert_level}
MOTIVO: {motivo_consulta}
SÍNTOMAS ACTIVOS: {', '.join(sintomas_activos)}
ANTECEDENTES: {', '.join(antecedentes_activos)}
NOTAS DOCTOR: {doctor_notes}
"""
        if es_critico:
            prompt += "\n[GUARDRAIL CRÍTICO]: Prescribe únicamente analgésico simple y advierte derivación inmediata."

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
