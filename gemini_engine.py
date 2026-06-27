"""
gemini_engine.py — Capa de IA Gemini para MED-INTELLIGENCE PRO

Complementa el motor bayesiano con razonamiento clínico avanzado en lenguaje natural.
Las redes bayesianas NO son sustituidas; Gemini actúa sobre los resultados probabilísticos
para enriquecer el análisis, el informe y el chatbot médico.

Arquitectura:
  [Bayes → P(E|síntomas)] → [GeminiDiagnosticLayer] → [Informe enriquecido + Sugerencias + Chat]
"""

import os
import json
import time
from google import genai
from google.genai import types

# ── CONFIGURACIÓN ────────────────────────────────────────────────────────────
_MODEL     = "gemini-2.5-flash"

# System prompt base — Médico Internista especializado
_SYSTEM_INTERNISTA = """Eres un médico internista especialista con amplia experiencia clínica.
Trabajas como motor de apoyo a la decisión clínica dentro del sistema MED-INTELLIGENCE PRO.
El sistema ya realizó un análisis probabilístico mediante redes bayesianas (Teorema de Bayes).
Tu rol es enriquecer ese análisis con razonamiento clínico narrativo de alto nivel.

Reglas estrictas:
1. NUNCA contradigas las probabilidades bayesianas directamente.
2. SIEMPRE añade valor clínico real: fisiopatología, correlaciones, contexto.
3. Responde en ESPAÑOL médico profesional, claro y conciso.
4. NO inventes medicamentos ni dosis no validadas clínicamente.
5. Si la situación es una emergencia (nivel ROJO), inclúyelo prominentemente.
6. Mantén el tono profesional pero humano.
7. Todos los valores numéricos de probabilidades que menciones vienen del análisis bayesiano — no los cambies."""

_SYSTEM_CHATBOT = """Eres el Médico Internista de Apoyo de MED-INTELLIGENCE PRO.
Ya tienes acceso al diagnóstico probabilístico bayesiano del paciente actual.
Tu misión es responder las dudas del médico o del personal de salud de forma clara, fundamentada y breve.

Reglas:
1. Responde en ESPAÑOL médico profesional.
2. Limita las respuestas a 2-4 párrafos máximo.
3. Fundamenta tus respuestas en el diagnóstico bayesiano provisto.
4. Si detectas señales de alarma en el contexto, menciónalas.
5. Añade siempre el disclaimer: "Este análisis es de apoyo clínico, no reemplaza el juicio médico."
6. NO reinventes el diagnóstico; complementa y clarifica."""

_SYSTEM_RECETAS = """Eres un asistente médico experto en farmacología y prescripción clínica de MED-INTELLIGENCE PRO.
Tu tarea es confeccionar una receta médica (prescripción) adecuada para el paciente a partir de su diagnóstico, constantes vitales, síntomas, antecedentes y nivel de alerta.

Reglas importantes:
1. Si el nivel de alerta (triage) es ROJO o indica una emergencia médica/quirúrgica inmediata:
   - Receta ÚNICAMENTE medicamentos para alivio sintomático inmediato y seguro (ej. analgésicos suaves como paracetamol, etc., evitando AINEs fuertes si hay sospecha de sangrado, etc.).
   - En el campo 'notes', escribe de forma prominente: '⚠️ ATENCIÓN: Se requiere evaluación médica de emergencia inmediata. Acuda al centro de salud más cercano.'
2. Para diagnósticos tratables de forma ambulatoria:
   - Prescribe medicamentos de primera línea validados clínicamente para el diagnóstico.
   - Especifica dosis estándar, frecuencia razonable (ej. 'Cada 8 horas', 'Una vez al día') y duración en días adecuada.
   - Calcula la cantidad total (quantity) necesaria para completar el tratamiento.
3. Evita prescribir dosis peligrosas o combinaciones redundantes.
4. Responde ÚNICAMENTE con un objeto JSON estructurado que contenga una lista de medicamentos en este formato (sin markdown ni texto extra):
{
  "medications": [
    {
      "medication": "Nombre del medicamento y presentación (ej. Amoxicilina 500mg)",
      "dosage": "Dosis por toma (ej. 1 cápsula)",
      "frequency": "Frecuencia de toma (ej. Cada 8 horas)",
      "duration_days": 7,
      "quantity": 21,
      "notes": "Instrucciones adicionales para el paciente (ej. Tomar después de las comidas)"
    }
  ]
}
"""


def _clean_json_response(raw_text: str) -> str:
    raw = raw_text.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines).strip()
    if raw.startswith("json"):
        raw = raw[4:].strip()
    return raw


class GeminiDiagnosticLayer:

    """
    Capa de enriquecimiento clínico con IA Gemini.
    Todos los métodos tienen fallback offline para garantizar disponibilidad.
    """

    def __init__(self):
        self.client = None
        self.client_rx = None
        self.available = False
        self.available_rx = False
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                self.client = genai.Client(api_key=api_key)
                self.available = True
            except Exception as e:
                print(f"[GeminiLayer] Error inicializando cliente estándar: {e}")
                
        api_key_rx = os.environ.get("GEMINI_API_KEY_RX") or api_key
        if api_key_rx:
            try:
                self.client_rx = genai.Client(api_key=api_key_rx)
                self.available_rx = True
            except Exception as e:
                print(f"[GeminiLayer] Error inicializando cliente de recetas: {e}")

    def _generar_config(self, temperature: float = 0.4) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=_SYSTEM_INTERNISTA,
            temperature=temperature,
            max_output_tokens=2048,
        )

    # ── 1. ANÁLISIS ENRIQUECIDO POST-BAYES ────────────────────────────────────
    def enriquecer_diagnostico_preliminar(
        self,
        probs_bayes: dict,
        sintomas: dict,
        constantes: dict,
        antecedentes: dict,
    ) -> dict:
        """
        Después del diagnóstico preliminar bayesiano, Gemini analiza el contexto y:
        - Valida clínicamente el top-3
        - Sugiere síntomas adicionales que no se preguntaron
        - Detecta alertas clínicas no cubiertas por Bayes
        - Genera un comentario de razonamiento breve

        Returns:
            dict con keys: validacion, sintomas_sugeridos, alertas_gemini,
                          confianza_gemini, fallback (bool)
        """
        if not self.available:
            return self._fallback_enriquecimiento(probs_bayes)

        # Top 5 diagnósticos bayesianos
        top5 = sorted(probs_bayes.items(), key=lambda x: x[1], reverse=True)[:5]
        top5_str = "\n".join([f"  {i+1}. {d}: {p*100:.2f}%" for i, (d, p) in enumerate(top5)])

        sintomas_presentes  = [s for s, v in sintomas.items() if v]
        antecedentes_activos = [a for a, v in antecedentes.items() if v]

        prompt = f"""El motor bayesiano procesó los datos del paciente y obtuvo:

TOP 5 DIAGNÓSTICOS BAYESIANOS:
{top5_str}

SÍNTOMAS PRESENTES: {', '.join(sintomas_presentes) if sintomas_presentes else 'Ninguno'}
ANTECEDENTES CLÍNICOS: {', '.join(antecedentes_activos) if antecedentes_activos else 'Ninguno'}
CONSTANTES VITALES:
  - Temperatura: {constantes.get('temperatura', '?')} °C
  - SpO2: {constantes.get('spo2', '?')} %
  - Presión Arterial: {constantes.get('pas', '?')}/{constantes.get('pad', '?')} mmHg
  - Frecuencia Cardíaca: {constantes.get('fc', '?')} bpm
  - Frecuencia Respiratoria: {constantes.get('fr', '?')} rpm
  - Edad: {constantes.get('edad', '?')} años

Tu tarea es responder EXACTAMENTE en el siguiente formato JSON (sin markdown, sin texto extra):
{{
  "validacion": "Comentario clínico breve (2-3 oraciones) sobre la coherencia del top diagnóstico con los síntomas y constantes",
  "sintomas_sugeridos": ["síntoma 1 que explorar", "síntoma 2", "síntoma 3"],
  "alertas_gemini": ["alerta clínica 1 si aplica", "alerta 2"],
  "confianza_gemini": "Alta / Media / Baja — con justificación en 1 oración"
}}

Si no hay alertas, usa lista vacía []. Máximo 4 síntomas sugeridos y 3 alertas."""

        try:
            response = self.client.models.generate_content(
                model=_MODEL,
                contents=prompt,
                config=self._generar_config(temperature=0.3),
            )
            raw = _clean_json_response(response.text)
            result = json.loads(raw)
            result["fallback"] = False
            return result
        except Exception as e:
            print(f"[GeminiLayer] Error en enriquecimiento: {e}")
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
        """
        Genera el informe clínico final integrando los resultados bayesianos.
        Devuelve el informe completo en markdown + la sección fisiopatológica
        generada por Gemini.

        Returns:
            dict con keys: informe_completo (str markdown), seccion_gemini (str),
                          fallback (bool)
        """
        if not self.available:
            return {"informe_completo": None, "seccion_gemini": None, "fallback": True}

        meta = meta_clinica or {}
        top3 = sorted(diagnosticos_diferenciales.items(), key=lambda x: x[1], reverse=True)[:3]
        diferenciales_str = "\n".join([f"  - {d}: {p*100:.2f}%" for d, p in top3 if d != diagnostico])

        alert_level = meta.get("alert_level", "Verde")
        emoji_nivel = {"Rojo": "🔴", "Amarillo": "🟡", "Verde": "🟢"}.get(alert_level, "🟢")

        prompt = f"""Genera el análisis fisiopatológico clínico para el siguiente caso médico.

DIAGNÓSTICO BAYESIANO FINAL: {diagnostico} ({probabilidad*100:.2f}% confianza)
NIVEL DE TRIAGE: {alert_level} {emoji_nivel}
TIPO DE VISITA: {tipo_visita.upper()}
MOTIVO DE CONSULTA: {motivo_consulta}

CONSTANTES VITALES:
  Temperatura: {constantes.get('temperatura', '?')} °C | SpO2: {constantes.get('spo2', '?')}%
  PA: {constantes.get('pas', '?')}/{constantes.get('pad', '?')} mmHg | FC: {constantes.get('fc', '?')} bpm
  FR: {constantes.get('fr', '?')} rpm | Edad: {constantes.get('edad', '?')} años

SÍNTOMAS PRESENTES: {', '.join(sintomas_activos) if sintomas_activos else 'Sin síntomas reportados'}
ANTECEDENTES: {', '.join(antecedentes_activos) if antecedentes_activos else 'Sin antecedentes relevantes'}

DIAGNÓSTICOS DIFERENCIALES (Bayesianos):
{diferenciales_str or '  Sin diferenciales significativos'}

Genera ÚNICAMENTE la sección de análisis fisiopatológico en markdown (sin encabezado, solo el contenido).
Incluye:
1. Por qué los síntomas y constantes son CONSISTENTES con {diagnostico} (fisiopatología concisa)
2. Por qué los diferenciales son MENOS probables en este contexto específico
3. Consideración clínica especial basada en los antecedentes (si aplica)
4. Una observación sobre la urgencia o el seguimiento recomendado

Máximo 250 palabras. Usa bullet points (*) para estructurar. Lenguaje médico profesional."""

        try:
            response = self.client.models.generate_content(
                model=_MODEL,
                contents=prompt,
                config=self._generar_config(temperature=0.5),
            )
            seccion_gemini = response.text.strip()
            return {
                "seccion_gemini": seccion_gemini,
                "fallback": False,
            }
        except Exception as e:
            print(f"[GeminiLayer] Error generando informe: {e}")
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
        """
        Chatbot médico que conoce el contexto bayesiano completo del paciente.

        Args:
            historial: lista de dicts [{role: 'user'|'model', text: '...'}]

        Returns:
            dict con keys: response (str), fallback (bool)
        """
        if not self.available:
            return {"response": self._fallback_chat(diagnostico, mensaje_usuario), "fallback": True}

        meta = meta_clinica or {}
        alert_level = meta.get("alert_level", "Verde")

        # Construir contexto del paciente como parte del system prompt
        system_con_contexto = f"""{_SYSTEM_CHATBOT}

=== CONTEXTO BAYESIANO DEL PACIENTE ACTUAL ===
Diagnóstico principal: {diagnostico} (Confianza Bayesiana: {probabilidad*100:.2f}%)
Nivel de Triage: {alert_level}
Síntomas presentes: {', '.join(sintomas_activos) if sintomas_activos else 'No registrados'}
Antecedentes: {', '.join(antecedentes_activos) if antecedentes_activos else 'Sin antecedentes'}
Constantes: Temp {constantes.get('temperatura','?')}°C | SpO2 {constantes.get('spo2','?')}% | PA {constantes.get('pas','?')}/{constantes.get('pad','?')} | FC {constantes.get('fc','?')} | FR {constantes.get('fr','?')}
Especialista sugerido: {meta.get('specialist', 'Medicina Interna')}
Summary clínico: {meta.get('summary', '')}
=== FIN DE CONTEXTO ==="""

        try:
            # Construir historial en formato Gemini
            formatted_history = []
            for msg in historial:
                formatted_history.append(
                    types.Content(
                        role=msg.get("role", "user"),
                        parts=[types.Part.from_text(text=msg.get("text", ""))]
                    )
                )

            chat = self.client.chats.create(
                model=_MODEL,
                config=types.GenerateContentConfig(
                    system_instruction=system_con_contexto,
                    temperature=0.6,
                    max_output_tokens=1024,
                ),
            )

            if formatted_history:
                chat._history = formatted_history

            response = chat.send_message(mensaje_usuario)
            return {"response": response.text, "fallback": False}

        except Exception as e:
            print(f"[GeminiLayer] Error en chat médico: {e}")
            return {"response": self._fallback_chat(diagnostico, mensaje_usuario), "fallback": True}

    def _fallback_chat(self, diagnostico: str, mensaje: str) -> str:
        msg = mensaje.lower()
        if any(w in msg for w in ["habito", "dieta", "comer", "reposo"]):
            return f"Para la recuperación de **{diagnostico}**, consulte el apartado de hábitos en el informe clínico. El asistente IA no está disponible en este momento."
        elif any(w in msg for w in ["medicamento", "pastilla", "dosis"]):
            return f"Consulte el apartado farmacológico del informe para **{diagnostico}**. Recuerde que los medicamentos deben ser prescritos por un médico. El asistente IA está temporalmente no disponible."
        elif any(w in msg for w in ["peligro", "emergencia", "alarma"]):
            return f"Revise las señales de alarma del informe para **{diagnostico}**. Ante cualquier deterioro súbito, acuda a urgencias inmediatamente. (Asistente IA no disponible temporalmente.)"
        return f"El asistente médico IA no está disponible en este momento. Consulte el informe clínico detallado para información sobre **{diagnostico}**."

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
        """
        Genera una sugerencia de receta médica estructurada con Gemini AI.
        """
        if not self.available_rx:
            return {"medications": [], "fallback": True}

        prompt = f"""Genera una receta para el siguiente caso clínico:

PACIENTE:
- Edad: {paciente_edad} años
- Género: {paciente_genero}

CASO CLÍNICO:
- Diagnóstico: {diagnostico}
- Nivel de Alerta: {alert_level}
- Motivo de Consulta: {motivo_consulta or "No especificado"}
- Notas del Doctor: {doctor_notes or "Ninguna"}

DATOS CLÍNICOS:
- Síntomas Activos: {', '.join(sintomas_activos) if sintomas_activos else 'Ninguno'}
- Antecedentes: {', '.join(antecedentes_activos) if antecedentes_activos else 'Ninguno'}
- Constantes Vitales:
  * Temperatura: {constantes.get('temperatura', '?')} °C
  * SpO2: {constantes.get('spo2', '?')} %
  * Presión Arterial: {constantes.get('pas', '?')}/{constantes.get('pad', '?')} mmHg
  * Frecuencia Cardíaca: {constantes.get('fc', '?')} bpm
  * Frecuencia Respiratoria: {constantes.get('fr', '?')} rpm

Tu tarea es responder EXACTAMENTE en el formato JSON especificado en las instrucciones del sistema, sin incluir bloques de código markdown ni texto adicional.
"""
        try:
            config = types.GenerateContentConfig(
                system_instruction=_SYSTEM_RECETAS,
                temperature=0.3,
                max_output_tokens=1024,
            )
            response = self.client_rx.models.generate_content(
                model=_MODEL,
                contents=prompt,
                config=config,
            )
            raw = _clean_json_response(response.text)
            result = json.loads(raw)
            result["fallback"] = False
            return result
        except Exception as e:
            print(f"[GeminiLayer] Error generando receta con IA: {e}")
            return {"medications": [], "fallback": True}

