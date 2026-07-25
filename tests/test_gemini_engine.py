import json
import os
import unittest
from unittest.mock import Mock, patch

from gemini_engine import GeminiDiagnosticLayer


class _FailingModels:
    def generate_content(self, **kwargs):
        raise RuntimeError("Gemini no disponible")


class _FailingChats:
    def create(self, **kwargs):
        raise RuntimeError("Chat de Gemini no disponible")


class _FailingClient:
    models = _FailingModels()
    chats = _FailingChats()


class _SuccessfulModels:
    def __init__(self, content):
        self.content = content

    def generate_content(self, **kwargs):
        return Mock(text=self.content)


class _SuccessfulClient:
    def __init__(self, content):
        self.models = _SuccessfulModels(content)


def _openrouter_response(content):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "choices": [{"message": {"content": content}}]
    }
    return response


class GeminiOpenRouterFallbackTests(unittest.TestCase):
    def setUp(self):
        self.layer = GeminiDiagnosticLayer.__new__(GeminiDiagnosticLayer)
        self.layer.client = _FailingClient()
        self.layer.available = True

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    @patch("gemini_engine.time.sleep", return_value=None)
    @patch("gemini_engine.requests.post")
    def test_chat_uses_openrouter_with_context_and_history(self, post, _sleep):
        post.return_value = _openrouter_response("Respuesta clínica desde OpenRouter")

        result = self.layer.chatear_medico(
            diagnostico="Gripe Común / Influenza",
            probabilidad=0.82,
            sintomas_activos=["Fiebre", "Tos"],
            antecedentes_activos=["Asma"],
            constantes={"temperatura": 38.2, "spo2": 97, "pas": 120, "pad": 80, "fc": 88},
            mensaje_usuario="¿Qué signos debo vigilar?",
            historial=[
                {"role": "user", "text": "Tengo fiebre."},
                {"role": "model", "text": "¿Desde cuándo?"},
            ],
            meta_clinica={"alert_level": "Verde"},
        )

        self.assertFalse(result["fallback"])
        self.assertEqual(result["response"], "Respuesta clínica desde OpenRouter")
        payload = post.call_args.kwargs["json"]
        self.assertEqual(payload["messages"][0]["role"], "system")
        self.assertEqual(payload["messages"][2]["role"], "assistant")
        self.assertEqual(payload["messages"][-1]["content"], "¿Qué signos debo vigilar?")

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    @patch("gemini_engine.time.sleep", return_value=None)
    @patch("gemini_engine.requests.post")
    def test_diagnostic_enrichment_uses_openrouter_json(self, post, _sleep):
        enrichment = {
            "validacion": "El cuadro es compatible con influenza.",
            "sintomas_sugeridos": ["Mialgias"],
            "alertas_gemini": [],
            "confianza_gemini": "Alta",
            "diagnostico_propuesto": None,
        }
        post.return_value = _openrouter_response(json.dumps(enrichment))

        result = self.layer.enriquecer_diagnostico_preliminar(
            probs_bayes={"Gripe Común / Influenza": 0.8, "Neumonía": 0.2},
            sintomas={"Fiebre": True, "Tos": True},
            constantes={"temperatura": 38.2, "spo2": 97, "pas": 120, "pad": 80, "fc": 88, "fr": 18, "edad": 30},
            antecedentes={"Asma": False},
            motivo_consulta="Fiebre y tos desde ayer",
        )

        self.assertFalse(result["fallback"])
        self.assertEqual(result["confianza_gemini"], "Alta")
        self.assertEqual(result["sintomas_sugeridos"], ["Mialgias"])

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    @patch("gemini_engine.time.sleep", return_value=None)
    @patch("gemini_engine.requests.post")
    def test_prescription_uses_openrouter_and_applies_allergy_guardrail(self, post, _sleep):
        prescription = {
            "medications": [{
                "medication": "Amoxicilina 500mg",
                "dosage": "1 cápsula",
                "frequency": "Cada 8 horas",
                "duration_days": 7,
                "quantity": 21,
                "notes": "Tomar con alimentos",
            }]
        }
        post.return_value = _openrouter_response(json.dumps(prescription))

        result = self.layer.generar_receta_con_ia(
            diagnostico="Faringoamigdalitis Aguda",
            motivo_consulta="Dolor de garganta",
            doctor_notes="Sin observaciones",
            constantes={"temperatura": 38.0},
            sintomas_activos=["Dolor de garganta"],
            antecedentes_activos=["Alergia a la penicilina"],
            paciente_edad=30,
            paciente_genero="Femenino",
            alert_level="Verde",
        )

        self.assertFalse(result["fallback"])
        medication = result["medications"][0]
        self.assertIn("Sustituto no penicilínico", medication["medication"])
        self.assertIn("AJUSTADO", medication["notes"])
        prompt = post.call_args.kwargs["json"]["messages"][-1]["content"]
        self.assertIn("medications", prompt)

    @patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"})
    @patch("gemini_engine.requests.post")
    def test_primary_gemini_response_skips_openrouter(self, post):
        prescription = {
            "medications": [{
                "medication": "Paracetamol 500mg",
                "dosage": "1 tableta",
                "frequency": "Cada 8 horas",
                "duration_days": 3,
                "quantity": 10,
                "notes": "Tomar si presenta fiebre",
            }]
        }
        self.layer.client = _SuccessfulClient(json.dumps(prescription))

        result = self.layer.generar_receta_con_ia(
            diagnostico="Gripe Común / Influenza",
            motivo_consulta="Fiebre",
            doctor_notes="Sin observaciones",
            constantes={"temperatura": 38.0},
            sintomas_activos=["Fiebre"],
            antecedentes_activos=[],
            paciente_edad=30,
            paciente_genero="Masculino",
            alert_level="Verde",
        )

        self.assertFalse(result["fallback"])
        self.assertEqual(result["medications"][0]["medication"], "Paracetamol 500mg")
        post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
