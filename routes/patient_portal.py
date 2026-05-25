import os
from flask import Blueprint, request, jsonify
from database import list_patients, add_patient
from utils import format_cedula
from google import genai
from google.genai import types

patient_portal_bp = Blueprint("patient_portal_bp", __name__)

# Configurar el cliente de Gemini
# Obtiene la API Key de las variables de entorno
api_key = os.environ.get("GEMINI_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """Eres MED-INTELLIGENCE, un asistente médico virtual amigable y profesional de la clínica.
Tu objetivo es realizar un triaje inicial a los pacientes mediante un chat.
Reglas:
1. Sé empático, profesional y claro.
2. Haz preguntas cortas para recopilar los síntomas principales del paciente, desde cuándo los tiene y su severidad.
3. No des un diagnóstico definitivo. Puedes sugerir posibles causas (pre-diagnóstico) pero SIEMPRE añade un descargo de responsabilidad indicando que debe consultar a un médico para una evaluación real.
4. Si detectas síntomas graves (dificultad para respirar grave, dolor de pecho, confusión, sangrado profuso), indícale al paciente que busque atención de emergencia inmediatamente.
5. Mantén tus respuestas relativamente cortas (máximo 2-3 párrafos).
"""

@patient_portal_bp.route("/api/portal/auth", methods=["POST"])
def portal_auth():
    data = request.json or {}
    cedula = data.get("cedula")
    if not cedula:
        return jsonify({"success": False, "error": "Cédula requerida."}), 400
    
    cedula = format_cedula(cedula)
    patients = list_patients(search=cedula)
    
    # Filtrar match exacto de cédula
    patient = next((p for p in patients if p.get("cedula") == cedula), None)
    if patient:
        return jsonify({"success": True, "patient": patient})
    return jsonify({"success": False, "error": "Paciente no encontrado."}), 404

@patient_portal_bp.route("/api/portal/register", methods=["POST"])
def portal_register():
    data = request.json or {}
    cedula = data.get("cedula")
    name = data.get("name")
    
    if not cedula or not name:
        return jsonify({"success": False, "error": "Nombre y cédula requeridos."}), 400
        
    cedula = format_cedula(cedula)
    patients = list_patients(search=cedula)
    if any(p.get("cedula") == cedula for p in patients):
        return jsonify({"success": False, "error": "El paciente ya está registrado."}), 400
        
    # Registro rápido: dob y gender se dejan por defecto, antecedentes vacíos
    success = add_patient(cedula, name, "1900-01-01", "Otro", antecedentes={}, phone="")
    if success:
        # Recuperar el paciente recién creado
        patients = list_patients(search=cedula)
        patient = next((p for p in patients if p.get("cedula") == cedula), None)
        return jsonify({"success": True, "patient": patient})
    return jsonify({"success": False, "error": "Error al registrar paciente."}), 500

@patient_portal_bp.route("/api/portal/chat", methods=["POST"])
def portal_chat():
    if not client:
        return jsonify({"success": False, "error": "La API de Gemini no está configurada en el servidor."}), 500
        
    data = request.json or {}
    message = data.get("message")
    history = data.get("history", []) # Lista de objetos { role: "user" | "model", parts: ["text"] }
    
    if not message:
        return jsonify({"success": False, "error": "Mensaje vacío."}), 400
        
    try:
        # Convertir el history del frontend al formato que espera google-genai
        formatted_history = []
        for msg in history:
            formatted_history.append(
                types.Content(
                    role=msg.get("role", "user"),
                    parts=[types.Part.from_text(text=msg.get("text", ""))]
                )
            )
            
        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            )
        )
        
        # Cargar historial
        if formatted_history:
            chat._history = formatted_history
            
        # Enviar nuevo mensaje
        response = chat.send_message(message)
        
        return jsonify({"success": True, "response": response.text})
    except Exception as e:
        print(f"Error en Gemini API: {e}")
        return jsonify({"success": False, "error": "Error al comunicar con el asistente médico."}), 500
