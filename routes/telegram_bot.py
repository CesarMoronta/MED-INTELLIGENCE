import os
import re
import json
import calendar
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from database import (get_connection, rows_to_dicts, list_users, 
                      add_patient, create_appointment, 
                      update_appointment_status, reschedule_appointment,
                      create_notification)

telegram_bp = Blueprint("telegram_bp", __name__)

# Persistent State Helpers using database instead of in-memory dictionary
def load_bot_state(chat_id: int) -> dict:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT state, user_data FROM dbo.telegram_bot_states WHERE chat_id = ?", chat_id)
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            state = row[0]
            user_data = json.loads(row[1]) if row[1] else {}
            user_data["state"] = state
            return user_data
    except Exception as e:
        print(f"Error loading bot state for chat {chat_id}: {e}")
    return {"state": "AWAITING_ACTION"}

def save_bot_state(chat_id: int, state_dict: dict):
    state = state_dict.get("state", "AWAITING_ACTION")
    user_data_copy = {k: v for k, v in state_dict.items() if k != "state"}
    user_data_json = json.dumps(user_data_copy)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            MERGE INTO dbo.telegram_bot_states AS target
            USING (SELECT ? AS chat_id) AS source
            ON target.chat_id = source.chat_id
            WHEN MATCHED THEN
                UPDATE SET state = ?, user_data = ?, updated_at = GETDATE()
            WHEN NOT MATCHED THEN
                INSERT (chat_id, state, user_data, updated_at)
                VALUES (source.chat_id, ?, ?, GETDATE());
        """, chat_id, state, user_data_json, state, user_data_json)
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error saving bot state for chat {chat_id}: {e}")

def get_bot_token():
    return os.environ.get("TELEGRAM_BOT_TOKEN")

def send_message(chat_id, text, reply_markup=None):
    token = get_bot_token()
    if not token:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def edit_message_reply_markup(chat_id, message_id, reply_markup):
    token = get_bot_token()
    if not token:
        return
    url = f"https://api.telegram.org/bot{token}/editMessageReplyMarkup"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": reply_markup
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error editing Telegram message reply markup: {e}")

def answer_callback_query(callback_query_id):
    token = get_bot_token()
    if not token:
        return
    url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
    payload = {
        "callback_query_id": callback_query_id
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error answering Telegram callback query: {e}")

def get_main_menu_markup():
    return {
        "keyboard": [
            [{"text": "📅 Agendar Cita"}],
            [{"text": "🔄 Mover Cita"}, {"text": "❌ Cancelar Cita"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def get_cancel_keyboard(custom_rows=None):
    kb = []
    if custom_rows:
        kb.extend(custom_rows)
    kb.append([{"text": "🔄 Cancelar / Reiniciar Proceso"}])
    return {"keyboard": kb, "resize_keyboard": True}

def calculate_age(dob_dt: datetime) -> int:
    today = datetime.now()
    return today.year - dob_dt.year - ((today.month, today.day) < (dob_dt.month, dob_dt.day))

# Interactive Calendar Builder
def create_calendar(year: int, month: int) -> dict:
    keyboard = []
    
    # Month/Year header and navigation buttons
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    month_name = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"][month - 1]
                  
    keyboard.append([
        {"text": "◀", "callback_data": f"CAL_NAV:{prev_year}:{prev_month}"},
        {"text": f"{month_name} {year}", "callback_data": "IGNORE"},
        {"text": "▶", "callback_data": f"CAL_NAV:{next_year}:{next_month}"}
    ])
    
    # Days of week header
    keyboard.append([
        {"text": "Lu", "callback_data": "IGNORE"},
        {"text": "Ma", "callback_data": "IGNORE"},
        {"text": "Mi", "callback_data": "IGNORE"},
        {"text": "Ju", "callback_data": "IGNORE"},
        {"text": "Vi", "callback_data": "IGNORE"},
        {"text": "Sa", "callback_data": "IGNORE"},
        {"text": "Do", "callback_data": "IGNORE"}
    ])
    
    # Weeks calendar grid
    cal = calendar.Calendar(firstweekday=0)
    month_weeks = cal.monthdayscalendar(year, month)
    for week in month_weeks:
        row = []
        for day in week:
            if day == 0:
                row.append({"text": " ", "callback_data": "IGNORE"})
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                row.append({"text": str(day), "callback_data": f"CAL_DAY:{date_str}"})
        keyboard.append(row)
        
    return {"inline_keyboard": keyboard}

# Helper Database Functions
def db_get_patient_by_cedula(cedula: str) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, dob, gender FROM dbo.patients WHERE cedula = ?", cedula)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "dob": str(row[2]), "gender": row[3]}
    return None

def db_get_patient_appointments(cedula: str) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.patient_id, a.doctor_id, a.scheduled_date, a.scheduled_time,
               a.status, p.name AS patient_name, u.full_name AS doctor_fullname
        FROM dbo.appointments a
        JOIN dbo.patients p ON a.patient_id = p.id
        JOIN dbo.users u ON a.doctor_id = u.id
        WHERE p.cedula = ? AND a.status = 'abierta'
        ORDER BY a.scheduled_date ASC, a.scheduled_time ASC
    """, cedula)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    return rows

def db_get_available_slots(doctor_id: int, date_str: str) -> list:
    from datetime import datetime
    
    # 1. Determinar día de la semana (1 = Lunes, ..., 7 = Domingo)
    try:
        day_num = datetime.strptime(date_str, "%Y-%m-%d").isoweekday()
    except ValueError:
        return []

    # 2. Consultar jornada laboral de la clínica
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT start_time, end_time, is_active FROM dbo.clinic_working_hours WHERE day_of_week = ?", day_num)
    clinic_row = cursor.fetchone()
    
    if not clinic_row or not clinic_row[2]:
        cursor.close()
        conn.close()
        return [] # Cerrado
        
    c_start = str(clinic_row[0])[:5]
    c_end = str(clinic_row[1])[:5]

    # 3. Consultar citas ocupadas
    cursor.execute("""
        SELECT scheduled_time 
        FROM dbo.appointments 
        WHERE doctor_id = ? AND CAST(scheduled_date AS DATE) = CAST(? AS DATE) AND status = 'abierta'
    """, doctor_id, date_str)
    taken_times = [str(r[0])[:5] for r in cursor.fetchall()]
    
    # 4. Consultar bloqueos de horario del doctor
    cursor.execute("""
        SELECT start_time, end_time 
        FROM dbo.doctor_blocked_slots
        WHERE doctor_id = ? AND CAST(blocked_date AS DATE) = CAST(? AS DATE)
    """, doctor_id, date_str)
    blocked_rows = cursor.fetchall()
    blocked_ranges = [(str(r[0])[:5], str(r[1])[:5]) for r in blocked_rows]
    
    cursor.close()
    conn.close()
    
    # Horarios estándar propuestos en el bot
    all_slots = ["08:00", "09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"]
    
    available = []
    for s in all_slots:
        # A. Dentro de la jornada de la clínica?
        if not (c_start <= s <= c_end):
            continue
            
        # B. Ya ocupado por una cita activa?
        if s in taken_times or (s + ":00") in taken_times:
            continue
            
        # C. Coincide con algún bloqueo del doctor?
        is_blocked = False
        for b_start, b_end in blocked_ranges:
            if b_start <= s <= b_end:
                is_blocked = True
                break
        if is_blocked:
            continue
            
        available.append(s)
    
    # Filtrar horas pasadas si la fecha seleccionada es hoy
    now = datetime.now()
    if date_str == now.strftime("%Y-%m-%d"):
        current_time = now.strftime("%H:%M")
        available = [s for s in available if s > current_time]
 
    return available

def db_get_active_doctors() -> list:
    users = list_users()
    doctors = [u for u in users if u.get("role") == "doctor" and u.get("is_active", True)]
    return doctors

def db_notify_secretaries_and_admins(message_text: str, from_user_id: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM dbo.users WHERE role IN ('secretaria', 'admin') AND is_active = 1")
        recipient_ids = [r[0] for r in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        for to_uid in recipient_ids:
            try:
                create_notification(
                    from_user_id=from_user_id,
                    to_user_id=to_uid,
                    message=message_text,
                    notif_type="citas"
                )
            except Exception as e:
                print(f"Error creating notification for user {to_uid}: {e}")
    except Exception as e:
        print(f"Error notifying secretaries: {e}")

# JCE Dominican Cédula API Integration with automatic retry
def jce_api_lookup(cedula: str, max_attempts: int = 2) -> dict | None:
    cedula_clean = re.sub(r"\D", "", cedula)
    base_url = os.environ.get("DGII_JCE_BASE_URL", "https://ecf-platform-backend-50801509587.us-central1.run.app")
    api_key  = os.environ.get("DGII_JCE_API_KEY", "")
    if not api_key:
        print("Warning: DGII_JCE_API_KEY is not configured in environment.")
        return None
    url = f"{base_url}/api/v1/dgii/jce?cedula={cedula_clean}"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    for attempt in range(1, max_attempts + 1):
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.ok:
                data = res.json()
                if data.get("found"):
                    gender_str = "Masculino" if data.get("sexo") == "M" else "Femenino" if data.get("sexo") == "F" else "Otro"
                    dob_raw = data.get("fechaNacimiento") or ""
                    dob_clean = dob_raw[:10] if len(dob_raw) >= 10 else "1990-01-01"
                    return {
                        "name": data.get("nombre"),
                        "dob": dob_clean,
                        "gender": gender_str
                    }
        except Exception as e:
            print(f"Intento {attempt}/{max_attempts} fallido al consultar JCE ({cedula_clean}): {e}")
        
        if attempt < max_attempts:
            import time
            time.sleep(1)

    return None

# Webhook Endpoint
@telegram_bp.route("/api/telegram/webhook", methods=["POST"])
def telegram_webhook():
    update = request.json or {}
    
    # A. HANDLE CALLBACK QUERY (Calendar navigation or selection)
    if "callback_query" in update:
        callback_query = update["callback_query"]
        callback_query_id = callback_query["id"]
        chat_id = callback_query["message"]["chat"]["id"]
        message_id = callback_query["message"]["message_id"]
        data = callback_query["data"]
        
        answer_callback_query(callback_query_id)
        
        if data == "IGNORE":
            return jsonify({"success": True})
            
        # Handle month navigation: CAL_NAV:2026:8
        if data.startswith("CAL_NAV:"):
            _, year, month = data.split(":")
            cal_markup = create_calendar(int(year), int(month))
            edit_message_reply_markup(chat_id, message_id, cal_markup)
            return jsonify({"success": True})
            
        # Handle day selection: CAL_DAY:2026-07-25
        if data.startswith("CAL_DAY:"):
            selected_date = data.split(":")[1]
            user_state = load_bot_state(chat_id)
            state = user_state["state"]
            
            if state == "AGENDAR_DOB":
                try:
                    dob_dt = datetime.strptime(selected_date, "%Y-%m-%d")
                    age = calculate_age(dob_dt)
                    if dob_dt > datetime.now():
                        send_message(chat_id, "⚠️ La fecha de nacimiento no puede ser una fecha futura. Por favor selecciona una fecha válida en el calendario:")
                        return jsonify({"success": True})
                    if age < 16:
                        cal_markup = create_calendar(1990, 1)
                        send_message(
                            chat_id,
                            f"⚠️ <b>Restricción de Edad:</b> El paciente debe ser <b>mayor de 16 años</b> para registrarse de forma independiente (edad seleccionada: <b>{age} años</b>).\n\n<i>(Si es un menor de edad, el registro debe realizarse en recepción por su tutor legal).</i>\n\nPor favor, selecciona una fecha de nacimiento válida en el calendario (mayor de 16 años):",
                            reply_markup=cal_markup
                        )
                        return jsonify({"success": True})
                    if age > 110:
                        cal_markup = create_calendar(1990, 1)
                        send_message(chat_id, "⚠️ La fecha seleccionada indica una edad superior a 110 años. Por favor selecciona una fecha de nacimiento válida:", reply_markup=cal_markup)
                        return jsonify({"success": True})
                except ValueError:
                    pass
                
                user_state["dob"] = selected_date
                user_state["state"] = "AGENDAR_GENDER"
                save_bot_state(chat_id, user_state)
                
                keyboard = get_cancel_keyboard([
                    [{"text": "Masculino"}, {"text": "Femenino"}, {"text": "Otro"}]
                ])
                send_message(chat_id, f"📅 Fecha de nacimiento seleccionada: <b>{selected_date}</b> (Edad: <b>{calculate_age(datetime.strptime(selected_date, '%Y-%m-%d'))} años</b>)\n\nPor favor, selecciona tu <b>Género</b>:", reply_markup=keyboard)

            elif state == "AGENDAR_DATE":
                try:
                    sel_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
                    if sel_date < datetime.now().date():
                        send_message(chat_id, "⚠️ No puedes seleccionar una fecha pasada. Por favor, elige hoy o una fecha futura en el calendario:")
                        return jsonify({"success": True})
                except ValueError:
                    pass

                slots = db_get_available_slots(user_state["doctor_id"], selected_date)
                if not slots:
                    send_message(chat_id, f"⚠️ El doctor no tiene turnos disponibles el <b>{selected_date}</b>. Por favor, selecciona otra fecha en el calendario:")
                    return jsonify({"success": True})
                
                user_state["date"] = selected_date
                user_state["state"] = "AGENDAR_TIME"
                save_bot_state(chat_id, user_state)
                
                rows = []
                row = []
                for idx, slot in enumerate(slots):
                    row.append({"text": slot})
                    if len(row) == 3 or idx == len(slots) - 1:
                        rows.append(row)
                        row = []
                keyboard = get_cancel_keyboard(rows)
                
                send_message(chat_id, f"📅 Fecha seleccionada: <b>{selected_date}</b>\n\nSelecciona la hora de la cita:", reply_markup=keyboard)
                
            elif state == "MOVER_DATE":
                try:
                    sel_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
                    if sel_date < datetime.now().date():
                        send_message(chat_id, "⚠️ No puedes seleccionar una fecha pasada. Por favor, elige hoy o una fecha futura en el calendario:")
                        return jsonify({"success": True})
                except ValueError:
                    pass

                slots = db_get_available_slots(user_state["doctor_id"], selected_date)
                if not slots:
                    send_message(chat_id, f"⚠️ El doctor no tiene turnos disponibles el <b>{selected_date}</b>. Selecciona otra fecha:")
                    return jsonify({"success": True})
                
                user_state["new_date"] = selected_date
                user_state["state"] = "MOVER_TIME"
                save_bot_state(chat_id, user_state)
                
                rows = []
                row = []
                for idx, slot in enumerate(slots):
                    row.append({"text": slot})
                    if len(row) == 3 or idx == len(slots) - 1:
                        rows.append(row)
                        row = []
                keyboard = get_cancel_keyboard(rows)
                
                send_message(chat_id, f"📅 Nueva fecha seleccionada: <b>{selected_date}</b>\n\nSelecciona la nueva hora:", reply_markup=keyboard)
                
            return jsonify({"success": True})

    # B. HANDLE TEXT MESSAGE
    if "message" not in update:
        return jsonify({"success": True})
    
    message = update["message"]
    chat_id = message["chat"]["id"]
    text = (message.get("text") or "").strip()
    text_lower = text.lower()
    
    # Check if the user wants to start over or cancel at any step
    cancel_keywords = ["/start", "/menu", "/cancel", "cancelar", "reiniciar", "🔄 reiniciar", "🔄 cancelar", "🔄 cancelar / reiniciar proceso", "🔄 cancelar / reiniciar"]
    if text_lower in cancel_keywords:
        prev_user_state = load_bot_state(chat_id)
        prev_state = prev_user_state.get("state", "AWAITING_ACTION")
        save_bot_state(chat_id, {"state": "AWAITING_ACTION"})
        
        if text_lower in ["/start", "/menu"] or prev_state == "AWAITING_ACTION":
            msg_text = "<b>🏥 Asistente Virtual MED-INTELLIGENCE</b>\n\n¡Bienvenido al sistema de agendamiento de citas! ¿En qué te puedo ayudar hoy?"
        else:
            msg_text = "<b>🏥 Asistente Virtual MED-INTELLIGENCE</b>\n\n🔄 Proceso cancelado. Has regresado al menú principal. ¿En qué te puedo ayudar?"

        send_message(
            chat_id, 
            msg_text, 
            reply_markup=get_main_menu_markup()
        )
        return jsonify({"success": True})

    # Retrieve current user state from database
    user_state = load_bot_state(chat_id)
    state = user_state["state"]

    # 1. MAIN MENU ACTION SELECTION
    if state == "AWAITING_ACTION":
        if text == "📅 Agendar Cita":
            save_bot_state(chat_id, {"state": "AGENDAR_CEDULA"})
            send_message(chat_id, "Por favor, ingresa tu número de <b>Cédula</b> (11 dígitos, sin guiones):", reply_markup=get_cancel_keyboard())
        elif text == "🔄 Mover Cita":
            save_bot_state(chat_id, {"state": "MOVER_CEDULA"})
            send_message(chat_id, "Por favor, ingresa tu número de <b>Cédula</b> (11 dígitos, sin guiones) para buscar tus citas:", reply_markup=get_cancel_keyboard())
        elif text == "❌ Cancelar Cita":
            save_bot_state(chat_id, {"state": "CANCELAR_CEDULA"})
            send_message(chat_id, "Por favor, ingresa tu número de <b>Cédula</b> (11 dígitos, sin guiones) para ver tus citas activas:", reply_markup=get_cancel_keyboard())
        else:
            send_message(chat_id, "Por favor, selecciona una opción del teclado o presiona /start para reiniciar.", reply_markup=get_main_menu_markup())

    # 2. FLOW: AGENDAR CITA - CEDULA
    elif state == "AGENDAR_CEDULA":
        cedula_clean = re.sub(r"\D", "", text)
        if len(cedula_clean) != 11:
            send_message(
                chat_id, 
                "⚠️ <b>Cédula inválida.</b> Debe contener exactamente 11 dígitos (ej: <code>03100012345</code> o <code>031-0001234-5</code>).\n\nPor favor, ingresa tu Cédula nuevamente:",
                reply_markup=get_cancel_keyboard()
            )
            return jsonify({"success": True})
        
        from utils import format_cedula
        formatted_cedula = format_cedula(cedula_clean)
        patient = db_get_patient_by_cedula(formatted_cedula)
        if patient:
            new_state = {
                "state": "AGENDAR_DOCTOR",
                "patient_id": patient["id"],
                "patient_name": patient["name"],
                "cedula": formatted_cedula
            }
            save_bot_state(chat_id, new_state)
            send_message(chat_id, f"Hola de nuevo, <b>{patient['name']}</b>.")
            
            doctors = db_get_active_doctors()
            if not doctors:
                send_message(chat_id, "Lo sentimos, no hay doctores disponibles en este momento.", reply_markup=get_main_menu_markup())
                save_bot_state(chat_id, {"state": "AWAITING_ACTION"})
                return jsonify({"success": True})
            
            rows = []
            for doc in doctors:
                rows.append([{"text": f"Dr. {doc['full_name']}"}])
            
            send_message(chat_id, "Selecciona el doctor con el que deseas agendar la cita:", reply_markup=get_cancel_keyboard(rows))
        else:
            send_message(chat_id, "🔍 Consultando cédula en la JCE...")
            jce_data = jce_api_lookup(formatted_cedula)
            
            if jce_data:
                # Check age requirement for JCE data
                try:
                    jce_dob_dt = datetime.strptime(jce_data["dob"], "%Y-%m-%d")
                    if calculate_age(jce_dob_dt) < 16:
                        send_message(
                            chat_id,
                            f"👤 <b>Persona encontrada en JCE:</b> {jce_data['name']}\n\n⚠️ <b>Restricción de Edad:</b> Según los registros de la JCE, eres menor de 16 años. No es posible realizar auto-registro de citas vía bot.\n\nPor favor acude a recepción con un padre o tutor legal.",
                            reply_markup=get_main_menu_markup()
                        )
                        save_bot_state(chat_id, {"state": "AWAITING_ACTION"})
                        return jsonify({"success": True})
                except Exception:
                    pass

                try:
                    patient_id = add_patient(
                        cedula=formatted_cedula,
                        name=jce_data["name"],
                        dob=jce_data["dob"],
                        gender=jce_data["gender"],
                        antecedentes={}
                    )
                    if not patient_id:
                        p = db_get_patient_by_cedula(formatted_cedula)
                        if p:
                            patient_id = p["id"]

                    if not patient_id:
                        raise Exception("No se pudo obtener el ID del paciente tras el registro.")

                    new_state = {
                        "state": "AGENDAR_DOCTOR",
                        "patient_id": patient_id,
                        "patient_name": jce_data["name"],
                        "cedula": formatted_cedula
                    }
                    save_bot_state(chat_id, new_state)
                    send_message(chat_id, f"👤 <b>Persona encontrada en JCE:</b> {jce_data['name']}\n✅ Te hemos registrado en el sistema automáticamente.")
                    
                    doctors = db_get_active_doctors()
                    rows = []
                    for doc in doctors:
                        rows.append([{"text": f"Dr. {doc['full_name']}"}])
                    
                    send_message(chat_id, "Selecciona el doctor con el que deseas agendar la cita:", reply_markup=get_cancel_keyboard(rows))
                except Exception as e:
                    send_message(chat_id, f"❌ Error al registrar desde la JCE: {e}", reply_markup=get_main_menu_markup())
                    save_bot_state(chat_id, {"state": "AWAITING_ACTION"})
            else:
                send_message(
                    chat_id,
                    "❌ <b>Cédula no encontrada en la JCE.</b>\n\nEl auto-registro de citas vía bot requiere que tu cédula esté validada en el padrón oficial de la JCE.\n\nPor favor acude a recepción de la clínica para registrar tus datos físicamente.",
                    reply_markup=get_main_menu_markup()
                )
                save_bot_state(chat_id, {"state": "AWAITING_ACTION"})

    # AGENDAR_NAME
    elif state == "AGENDAR_NAME":
        name_clean = text.strip()
        words = name_clean.split()
        is_valid_chars = bool(re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s'-]{5,}$", name_clean))
        if len(words) < 2 or not is_valid_chars:
            send_message(
                chat_id,
                "⚠️ <b>Nombre no válido.</b> Por favor ingresa tu <b>Nombre y Apellido completos</b> (mínimo dos palabras, solo letras. Ej: <i>Wilson Pérez</i>):",
                reply_markup=get_cancel_keyboard()
            )
            return jsonify({"success": True})
        
        user_state["patient_name"] = name_clean.upper()
        user_state["state"] = "AGENDAR_DOB"
        save_bot_state(chat_id, user_state)
        
        cal_markup = create_calendar(1990, 1)
        send_message(chat_id, "Cargando calendario...", reply_markup={"remove_keyboard": True})
        send_message(
            chat_id, 
            "¿Cuál es tu <b>Fecha de Nacimiento</b>? <i>(Debes ser mayor de 16 años)</i>\n\nSelecciona la fecha en el calendario (usa ◀ y ▶ para cambiar de mes/año, o escríbela en formato <code>AAAA-MM-DD</code>):", 
            reply_markup=cal_markup
        )

    # AGENDAR_DOB
    elif state == "AGENDAR_DOB":
        is_valid_date = False
        error_msg = None
        if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
            try:
                dob_dt = datetime.strptime(text, "%Y-%m-%d")
                age = calculate_age(dob_dt)
                if dob_dt > datetime.now():
                    error_msg = "⚠️ La fecha de nacimiento no puede ser una fecha futura."
                elif age < 16:
                    error_msg = f"⚠️ <b>Restricción de Edad:</b> El paciente debe ser <b>mayor de 16 años</b> (edad indicada: {age} años).\n<i>(Si es un menor de edad, el registro debe ser realizado en recepción con su tutor legal).</i>"
                elif age > 110:
                    error_msg = "⚠️ La fecha ingresada indica una edad superior a 110 años."
                else:
                    is_valid_date = True
            except ValueError:
                error_msg = "⚠️ La fecha especificada no existe en el calendario (ej: febrero 30)."

        if not is_valid_date:
            cal_markup = create_calendar(1990, 1)
            msg = error_msg or "⚠️ Formato o fecha no válida. Por favor selecciona tu fecha en el calendario o escríbela en formato <code>AAAA-MM-DD</code> (ej. 1990-05-15):"
            send_message(chat_id, f"{msg}\n\nPor favor, inténtalo de nuevo:", reply_markup=cal_markup)
            return jsonify({"success": True})
        
        user_state["dob"] = text
        user_state["state"] = "AGENDAR_GENDER"
        save_bot_state(chat_id, user_state)
        keyboard = get_cancel_keyboard([
            [{"text": "Masculino"}, {"text": "Femenino"}, {"text": "Otro"}]
        ])
        send_message(chat_id, f"📅 Fecha de nacimiento seleccionada: <b>{text}</b> (Edad: <b>{calculate_age(datetime.strptime(text, '%Y-%m-%d'))} años</b>)\n\nPor favor, selecciona tu <b>Género</b>:", reply_markup=keyboard)

    # AGENDAR_GENDER
    elif state == "AGENDAR_GENDER":
        if text not in ["Masculino", "Femenino", "Otro"]:
            keyboard = get_cancel_keyboard([
                [{"text": "Masculino"}, {"text": "Femenino"}, {"text": "Otro"}]
            ])
            send_message(chat_id, "⚠️ Por favor, selecciona un género válido de las opciones disponibles:", reply_markup=keyboard)
            return jsonify({"success": True})
        
        try:
            patient_id = add_patient(
                cedula=user_state["cedula"],
                name=user_state["patient_name"],
                dob=user_state["dob"],
                gender=text,
                antecedentes={}
            )
            if not patient_id:
                p = db_get_patient_by_cedula(user_state["cedula"])
                if p:
                    patient_id = p["id"]

            if not patient_id:
                raise Exception("No se pudo obtener el ID del paciente tras el registro.")

            user_state["patient_id"] = patient_id
            user_state["state"] = "AGENDAR_DOCTOR"
            save_bot_state(chat_id, user_state)
            send_message(chat_id, "✅ Registro de paciente completado con éxito.")
            
            doctors = db_get_active_doctors()
            rows = []
            for doc in doctors:
                rows.append([{"text": f"Dr. {doc['full_name']}"}])
            
            send_message(chat_id, "Selecciona el doctor con el que deseas agendar la cita:", reply_markup=get_cancel_keyboard(rows))
        except Exception as e:
            send_message(chat_id, f"❌ Error al registrar paciente: {e}", reply_markup=get_main_menu_markup())
            save_bot_state(chat_id, {"state": "AWAITING_ACTION"})

    # AGENDAR_DOCTOR
    elif state == "AGENDAR_DOCTOR":
        doctors = db_get_active_doctors()
        valid_doctor = False
        
        # 1. Intentar por ID si estuviera en el formato (para retrocompatibilidad)
        match = re.search(r"\(ID:\s*(\d+)\)", text)
        if match:
            doc_id = int(match.group(1))
            for d in doctors:
                if d["id"] == doc_id:
                    valid_doctor = True
                    user_state["doctor_id"] = doc_id
                    user_state["doctor_name"] = text.split(" (")[0]
                    user_state["state"] = "AGENDAR_DATE"
                    save_bot_state(chat_id, user_state)
                    break
        else:
            # 2. Buscar por coincidencia de nombre (nuevo formato sin ID visible)
            clean_input = text.replace("Dr.", "").replace("dr.", "").replace("Dr", "").replace("dr", "").strip().lower()
            for d in doctors:
                doc_name = d.get("full_name", "").strip().lower()
                doc_username = d.get("username", "").strip().lower()
                if doc_name == clean_input or doc_username == clean_input or clean_input in doc_name or doc_name in clean_input:
                    valid_doctor = True
                    user_state["doctor_id"] = d["id"]
                    user_state["doctor_name"] = f"Dr. {d['full_name']}"
                    user_state["state"] = "AGENDAR_DATE"
                    save_bot_state(chat_id, user_state)
                    break

        if not valid_doctor:
            rows = []
            for doc in doctors:
                rows.append([{"text": f"Dr. {doc['full_name']}"}])
            send_message(chat_id, "⚠️ Por favor, selecciona un doctor válido usando la lista de botones:", reply_markup=get_cancel_keyboard(rows))
            return jsonify({"success": True})
        
        now = datetime.now()
        cal_markup = create_calendar(now.year, now.month)
        
        send_message(chat_id, "Cargando calendario...", reply_markup={"remove_keyboard": True})
        send_message(chat_id, "Selecciona la fecha para la cita en el calendario:", reply_markup=cal_markup)

    # AGENDAR_TIME
    elif state == "AGENDAR_TIME":
        slots = db_get_available_slots(user_state["doctor_id"], user_state["date"])
        if text not in slots:
            rows = []
            row = []
            for idx, slot in enumerate(slots):
                row.append({"text": slot})
                if len(row) == 3 or idx == len(slots) - 1:
                    rows.append(row)
                    row = []
            send_message(chat_id, "⚠️ Por favor selecciona una hora disponible usando los botones de abajo:", reply_markup=get_cancel_keyboard(rows))
            return jsonify({"success": True})
        
        user_state["time"] = text
        user_state["state"] = "AGENDAR_MOTIVO"
        save_bot_state(chat_id, user_state)
        
        send_message(
            chat_id,
            "📝 Por favor, escribe brevemente el <b>motivo o síntoma principal</b> de tu visita (ej: Dolor de cabeza, chequeo general):",
            reply_markup=get_cancel_keyboard()
        )

    # AGENDAR_MOTIVO
    elif state == "AGENDAR_MOTIVO":
        motivo = text.strip()
        if not motivo:
            send_message(
                chat_id,
                "⚠️ El motivo no puede estar vacío. Por favor, escribe el motivo o síntoma de tu visita:",
                reply_markup=get_cancel_keyboard()
            )
            return jsonify({"success": True})
        
        try:
            create_appointment(
                patient_id=user_state["patient_id"],
                doctor_id=user_state["doctor_id"],
                scheduled_date=user_state["date"],
                scheduled_time=user_state["time"],
                notes=motivo
            )
            send_message(
                chat_id,
                f"🎉 <b>¡Cita Confirmada!</b>\n\n"
                f"👤 <b>Paciente:</b> {user_state['patient_name']}\n"
                f"👨‍⚕️ <b>Médico:</b> {user_state['doctor_name']}\n"
                f"📅 <b>Fecha:</b> {user_state['date']}\n"
                f"⏰ <b>Hora:</b> {user_state['time']}\n"
                f"📝 <b>Motivo:</b> {motivo}\n\n"
                f"¡Te esperamos!",
                reply_markup=get_main_menu_markup()
            )
            msg_notif = f"📅 Nueva cita vía Telegram: {user_state['patient_name']} con el {user_state['doctor_name']} para el {user_state['date']} a las {user_state['time']} - Motivo: {motivo}"
            db_notify_secretaries_and_admins(msg_notif, user_state["doctor_id"])
        except Exception as e:
            send_message(chat_id, f"❌ Error al crear la cita: {e}", reply_markup=get_main_menu_markup())
        
        save_bot_state(chat_id, {"state": "AWAITING_ACTION"})

    # 3. FLOW: MOVER CITA
    elif state == "MOVER_CEDULA":
        cedula_clean = re.sub(r"\D", "", text)
        if len(cedula_clean) != 11:
            send_message(
                chat_id, 
                "⚠️ <b>Cédula inválida.</b> Debe contener exactamente 11 dígitos (ej: <code>03100012345</code> o <code>031-0001234-5</code>).\n\nPor favor, ingresa tu Cédula nuevamente:",
                reply_markup=get_cancel_keyboard()
            )
            return jsonify({"success": True})

        from utils import format_cedula
        formatted_cedula = format_cedula(cedula_clean)
        appointments = db_get_patient_appointments(formatted_cedula)
        if not appointments:
            send_message(chat_id, "⚠️ No tienes ninguna cita activa agendada.", reply_markup=get_main_menu_markup())
            save_bot_state(chat_id, {"state": "AWAITING_ACTION"})
            return jsonify({"success": True})
        
        serializable_apps = {}
        rows = []
        for app in appointments:
            app_copy = dict(app)
            app_copy["scheduled_date"] = str(app["scheduled_date"])
            app_copy["scheduled_time"] = str(app["scheduled_time"])
            serializable_apps[str(app["id"])] = app_copy
            rows.append([{"text": f"Cita #{app['id']} - {app['scheduled_date']} {str(app['scheduled_time'])[:5]} con {app['doctor_fullname']}"}])
            
        user_state["state"] = "MOVER_SELECTION"
        user_state["appointments"] = serializable_apps
        save_bot_state(chat_id, user_state)
        
        send_message(chat_id, "Selecciona cuál de tus citas deseas reprogramar:", reply_markup=get_cancel_keyboard(rows))

    elif state == "MOVER_SELECTION":
        match = re.match(r"^Cita\s*#\s*(\d+)", text)
        if not match or match.group(1) not in user_state.get("appointments", {}):
            rows = []
            for app_id, app in user_state.get("appointments", {}).items():
                rows.append([{"text": f"Cita #{app_id} - {app['scheduled_date']} {str(app['scheduled_time'])[:5]} con {app['doctor_fullname']}"}])
            send_message(chat_id, "⚠️ Por favor, selecciona una cita válida de la lista:", reply_markup=get_cancel_keyboard(rows))
            return jsonify({"success": True})
        
        app_id = match.group(1)
        selected_app = user_state["appointments"][app_id]
        user_state["appointment_id"] = int(app_id)
        user_state["doctor_id"] = selected_app["doctor_id"]
        user_state["state"] = "MOVER_DATE"
        save_bot_state(chat_id, user_state)
        
        now = datetime.now()
        cal_markup = create_calendar(now.year, now.month)
        
        send_message(chat_id, "Cargando calendario...", reply_markup={"remove_keyboard": True})
        send_message(chat_id, "Selecciona la nueva fecha deseada en el calendario:", reply_markup=cal_markup)

    elif state == "MOVER_TIME":
        slots = db_get_available_slots(user_state["doctor_id"], user_state["new_date"])
        if text not in slots:
            rows = []
            row = []
            for idx, slot in enumerate(slots):
                row.append({"text": slot})
                if len(row) == 3 or idx == len(slots) - 1:
                    rows.append(row)
                    row = []
            send_message(chat_id, "⚠️ Por favor, selecciona una hora válida de las opciones de abajo:", reply_markup=get_cancel_keyboard(rows))
            return jsonify({"success": True})
        
        try:
            reschedule_appointment(
                appointment_id=user_state["appointment_id"],
                new_date=user_state["new_date"],
                new_time=text
            )
            send_message(chat_id, f"✅ <b>¡Cita Reprogramada con éxito!</b>\n\nTu cita ahora quedó para el día <b>{user_state['new_date']} a las {text}</b>.", reply_markup=get_main_menu_markup())
            msg_notif = f"🔄 Cita #{user_state['appointment_id']} reprogramada vía Telegram para el {user_state['new_date']} a las {text}"
            db_notify_secretaries_and_admins(msg_notif, user_state["doctor_id"])
        except Exception as e:
            send_message(chat_id, f"❌ Error al mover la cita: {e}", reply_markup=get_main_menu_markup())
            
        save_bot_state(chat_id, {"state": "AWAITING_ACTION"})

    # 4. FLOW: CANCELAR CITA
    elif state == "CANCELAR_CEDULA":
        cedula_clean = re.sub(r"\D", "", text)
        if len(cedula_clean) != 11:
            send_message(
                chat_id, 
                "⚠️ <b>Cédula inválida.</b> Debe contener exactamente 11 dígitos (ej: <code>03100012345</code> o <code>031-0001234-5</code>).\n\nPor favor, ingresa tu Cédula nuevamente:",
                reply_markup=get_cancel_keyboard()
            )
            return jsonify({"success": True})

        from utils import format_cedula
        formatted_cedula = format_cedula(cedula_clean)
        appointments = db_get_patient_appointments(formatted_cedula)
        if not appointments:
            send_message(chat_id, "⚠️ No tienes ninguna cita activa para cancelar.", reply_markup=get_main_menu_markup())
            save_bot_state(chat_id, {"state": "AWAITING_ACTION"})
            return jsonify({"success": True})
        
        serializable_apps = {}
        rows = []
        for app in appointments:
            app_copy = dict(app)
            app_copy["scheduled_date"] = str(app["scheduled_date"])
            app_copy["scheduled_time"] = str(app["scheduled_time"])
            serializable_apps[str(app["id"])] = app_copy
            rows.append([{"text": f"Cancelar Cita #{app['id']} - {app['scheduled_date']} con {app['doctor_fullname']}"}])
            
        user_state["state"] = "CANCELAR_SELECTION"
        user_state["appointments"] = serializable_apps
        save_bot_state(chat_id, user_state)
        
        send_message(chat_id, "Selecciona cuál de tus citas deseas cancelar:", reply_markup=get_cancel_keyboard(rows))

    elif state == "CANCELAR_SELECTION":
        match = re.match(r"^Cancelar Cita\s*#\s*(\d+)", text)
        if not match or match.group(1) not in user_state.get("appointments", {}):
            rows = []
            for app_id, app in user_state.get("appointments", {}).items():
                rows.append([{"text": f"Cancelar Cita #{app_id} - {app['scheduled_date']} con {app['doctor_fullname']}"}])
            send_message(chat_id, "⚠️ Por favor, selecciona una cita válida de la lista:", reply_markup=get_cancel_keyboard(rows))
            return jsonify({"success": True})
        
        app_id = int(match.group(1))
        selected_app = user_state["appointments"][str(app_id)]
        try:
            update_appointment_status(app_id, "cancelada")
            send_message(chat_id, f"✅ La cita #{app_id} ha sido <b>Cancelada</b> exitosamente.", reply_markup=get_main_menu_markup())
            msg_notif = f"❌ Cita #{app_id} cancelada vía Telegram"
            db_notify_secretaries_and_admins(msg_notif, selected_app["doctor_id"])
        except Exception as e:
            send_message(chat_id, f"❌ Error al cancelar la cita: {e}", reply_markup=get_main_menu_markup())
            
        save_bot_state(chat_id, {"state": "AWAITING_ACTION"})

    return jsonify({"success": True})
