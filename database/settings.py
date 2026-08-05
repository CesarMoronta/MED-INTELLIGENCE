import json
from datetime import datetime, date
from database.connection import get_connection, get_db_cursor, rows_to_dicts, _fmt_date, MAX_LOGIN_ATTEMPTS, LOCKOUT_MINUTES
import copy
from database.users import create_user
from database.patients import add_patient

SETTINGS_KEYS = [
    "clinic_name", "clinic_rnc", "clinic_address", "clinic_phone", 
    "dgii_url", "dgii_api_key", "ui_primary_color", "ui_primary_color_hover",
    "theme_mode", "billing_note_type"
]

def initialize_database(seed_patients=None, default_priors=None, default_conditionals=None):
    """
    Verifica que el schema ya exista (debe ejecutarse database_schema.txt antes).
    Hace el seeding inicial: admin, pacientes de prueba, priors del motor Bayes.
    """
    # Ejecutar scripts de migración/actualización automáticos para sincronizar la base de datos
    print("🔄 Verificando y aplicando actualizaciones de base de datos...")
    try:
        import update_db_subscription
        update_db_subscription.apply_updates()
    except Exception as e:
        print(f"⚠️ Error al aplicar update_db_subscription: {e}")

    try:
        import update_db_v3_1
        update_db_v3_1.apply_updates()
    except Exception as e:
        print(f"⚠️ Error al aplicar update_db_v3_1: {e}")

    try:
        import update_db_visits
        update_db_visits.apply_migration()
    except Exception as e:
        print(f"⚠️ Error al aplicar update_db_visits: {e}")

    try:
        import update_db_vw_visits
        update_db_vw_visits.apply_migration()
    except Exception as e:
        print(f"⚠️ Error al aplicar update_db_vw_visits: {e}")

    try:
        import update_db_billing_info
        update_db_billing_info.apply_updates()
    except Exception as e:
        print(f"⚠️ Error al aplicar update_db_billing_info: {e}")

    try:
        import update_db_schedules
        update_db_schedules.apply_migration()
    except Exception as e:
        print(f"⚠️ Error al aplicar update_db_schedules: {e}")

    try:
        import update_db_reporting_demographics
        update_db_reporting_demographics.apply_migration()
    except Exception as e:
        print(f"⚠️ Error al aplicar update_db_reporting_demographics: {e}")

    conn   = get_connection()
    cursor = conn.cursor()

    # Admin por defecto
    cursor.execute("SELECT COUNT(1) FROM dbo.users")
    if cursor.fetchone()[0] == 0:
        create_user("Admin", "Admin", "admin", full_name="Administrador del Sistema")

    # Pacientes de prueba
    cursor.execute("SELECT COUNT(1) FROM dbo.patients")
    if cursor.fetchone()[0] == 0 and seed_patients:
        for p in seed_patients:
            add_patient(
                cedula=p.get("cedula", ""),
                name=p["name"],
                dob=p["dob"],
                gender=p["gender"],
                antecedentes=p.get("antecedentes", {}),
                registered_by=None
            )

    # Priors del modelo
    cursor.execute("SELECT COUNT(1) FROM dbo.model_priors")
    if cursor.fetchone()[0] == 0 and default_priors and default_conditionals:
        reset_parameters(default_priors, default_conditionals)

    cursor.close()
    conn.close()

    # Vistas adicionales del módulo de reportes (idempotente)
    ensure_reports_views()

def get_parameters() -> dict | None:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT disease, prior FROM dbo.model_priors")
    priors = {r[0]: float(r[1]) for r in cursor.fetchall()}
    cursor.execute("SELECT sintoma, disease, p FROM dbo.model_conditionals")
    conditionals: dict = {}
    for sintoma, disease, p in cursor.fetchall():
        conditionals.setdefault(sintoma, {})[disease] = float(p)
    cursor.close()
    conn.close()
    if not priors or not conditionals:
        return None
    return {"priors": priors, "conditionals": conditionals}

def save_parameters(priors: dict, conditionals: dict) -> bool:
    conn   = get_connection()
    cursor = conn.cursor()
    for disease, prior in priors.items():
        cursor.execute(
            "IF EXISTS (SELECT 1 FROM dbo.model_priors WHERE disease=?) "
            "  UPDATE dbo.model_priors SET prior=?, updated_at=SYSUTCDATETIME() WHERE disease=? "
            "ELSE "
            "  INSERT INTO dbo.model_priors (disease, prior) VALUES (?, ?)",
            disease, prior, disease, disease, prior
        )
    for sintoma, distrib in conditionals.items():
        for disease, p in distrib.items():
            cursor.execute(
                "IF EXISTS (SELECT 1 FROM dbo.model_conditionals WHERE sintoma=? AND disease=?) "
                "  UPDATE dbo.model_conditionals SET p=?, updated_at=SYSUTCDATETIME() WHERE sintoma=? AND disease=? "
                "ELSE "
                "  INSERT INTO dbo.model_conditionals (sintoma, disease, p) VALUES (?, ?, ?)",
                sintoma, disease, p, sintoma, disease, sintoma, disease, p
            )
    cursor.close()
    conn.close()
    return True

def reset_parameters(default_priors: dict, default_conditionals: dict) -> bool:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dbo.model_priors")
    cursor.execute("DELETE FROM dbo.model_conditionals")
    for disease, prior in default_priors.items():
        cursor.execute(
            "INSERT INTO dbo.model_priors (disease, prior) VALUES (?, ?)", disease, prior
        )
    for sintoma, distrib in default_conditionals.items():
        for disease, p in distrib.items():
            cursor.execute(
                "INSERT INTO dbo.model_conditionals (sintoma, disease, p) VALUES (?, ?, ?)",
                sintoma, disease, p
            )
    cursor.close()
    conn.close()
    return True

def get_clinic_name() -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key_value FROM dbo.system_config WHERE key_name = 'clinic_name'")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else "Consultorio Médico"

def set_clinic_name(name: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "IF EXISTS (SELECT 1 FROM dbo.system_config WHERE key_name='clinic_name') "
        "  UPDATE dbo.system_config SET key_value=?, updated_at=SYSUTCDATETIME() WHERE key_name='clinic_name' "
        "ELSE "
        "  INSERT INTO dbo.system_config (key_name, key_value) VALUES ('clinic_name', ?)",
        name, name
    )
    cursor.close()
    conn.close()

def get_all_clinic_settings() -> dict:
    """Retorna todos los ajustes del consultorio como dict {key: value}."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key_name, key_value FROM dbo.system_config")
    settings = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    # Defaults
    defaults = {k: "" for k in SETTINGS_KEYS}
    defaults["clinic_name"] = "Consultorio Médico"
    defaults.update(settings)
    return defaults

def set_clinic_settings(settings: dict):
    """Guarda múltiples ajustes en batch."""
    conn   = get_connection()
    cursor = conn.cursor()
    for key, value in settings.items():
        cursor.execute(
            "IF EXISTS (SELECT 1 FROM dbo.system_config WHERE key_name=?) "
            "  UPDATE dbo.system_config SET key_value=?, updated_at=SYSUTCDATETIME() WHERE key_name=? "
            "ELSE "
            "  INSERT INTO dbo.system_config (key_name, key_value) VALUES (?, ?)",
            key, value, key, key, value
        )
    cursor.close()
    conn.close()

def get_notifications(user_id: int, limit: int = 30) -> list:
    """Obtiene notificaciones del usuario (recibidas o enviadas por él)."""
    conn   = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""SELECT TOP ({limit})
                   n.id, n.from_user_id, n.to_user_id, n.message,
                   n.type, n.is_read, n.created_at,
                   uf.full_name AS from_name,
                   ut.full_name AS to_name
               FROM dbo.notifications n
               LEFT JOIN dbo.users uf ON uf.id = n.from_user_id
               LEFT JOIN dbo.users ut ON ut.id = n.to_user_id
               WHERE n.to_user_id = ? OR n.from_user_id = ?
               ORDER BY n.created_at DESC""",
            user_id, user_id
        )
        rows = rows_to_dicts(cursor)
    except Exception:
        rows = []
    finally:
        cursor.close()
        conn.close()
    for r in rows:
        r["created_at"] = _fmt_date(r.get("created_at"))
        r["is_read"]    = bool(r.get("is_read", False))
    return rows

def get_unread_count(user_id: int) -> int:
    conn   = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(1) FROM dbo.notifications WHERE to_user_id=? AND is_read=0",
            user_id
        )
        row = cursor.fetchone()
    except Exception:
        row = None
    finally:
        cursor.close()
        conn.close()
    return row[0] if row else 0

def create_notification(from_user_id: int, to_user_id: int,
                        message: str, notif_type: str = "message") -> int:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO dbo.notifications (from_user_id, to_user_id, message, type) "
        "OUTPUT INSERTED.id VALUES (?, ?, ?, ?)",
        from_user_id, to_user_id, message, notif_type
    )
    nid = int(cursor.fetchone()[0])
    cursor.close()
    conn.close()
    return nid

def mark_notification_read(notification_id: int):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE dbo.notifications SET is_read=1 WHERE id=?", notification_id
    )
    cursor.close()
    conn.close()

def mark_all_notifications_read(user_id: int):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE dbo.notifications SET is_read=1 WHERE to_user_id=?", user_id
    )
    cursor.close()
    conn.close()

def ensure_reports_views():
    """
    Crea la vista vw_reports_waiting_time si no existe.
    Se llama desde initialize_database() de forma segura (no-op si ya existe).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            IF OBJECT_ID(N'dbo.vw_reports_waiting_time', N'V') IS NULL
            EXEC(N'
                CREATE VIEW dbo.vw_reports_waiting_time AS
                SELECT
                    a.id            AS appointment_id,
                    a.patient_id,
                    p.name          AS patient_name,
                    a.doctor_id,
                    u.full_name     AS doctor_fullname,
                    a.scheduled_date,
                    a.scheduled_time,
                    ev.visit_date   AS actual_arrival,
                    DATEDIFF(MINUTE,
                        CAST(
                            CONVERT(NVARCHAR(10), a.scheduled_date, 120)
                            + N'' ''
                            + CONVERT(NVARCHAR(8), a.scheduled_time, 108)
                        AS DATETIME2),
                        ev.visit_date
                    ) AS wait_minutes,
                    a.status        AS appointment_status
                FROM dbo.appointments a
                JOIN dbo.patients p          ON a.patient_id = p.id
                JOIN dbo.users    u          ON a.doctor_id  = u.id
                LEFT JOIN dbo.emergency_visits ev ON ev.appointment_id = a.id
            ')
        """)
    except Exception as e:
        print(f"[ensure_reports_views] {e}")
    finally:
        cursor.close()
        conn.close()

def get_clinic_working_hours() -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT day_of_week, start_time, end_time, is_active FROM dbo.clinic_working_hours ORDER BY day_of_week")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    res = []
    for r in rows:
        res.append({
            "day_of_week": r[0],
            "start_time": str(r[1])[:5] if r[1] else "08:00",
            "end_time": str(r[2])[:5] if r[2] else "18:00",
            "is_active": bool(r[3])
        })
    return res

def save_clinic_working_hours(hours_list: list) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        for item in hours_list:
            day = int(item.get("day_of_week"))
            start = str(item.get("start_time"))
            end = str(item.get("end_time"))
            is_act = 1 if item.get("is_active") else 0
            
            cursor.execute(
                "UPDATE dbo.clinic_working_hours SET start_time = ?, end_time = ?, is_active = ? WHERE day_of_week = ?",
                start, end, is_act, day
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"[save_clinic_working_hours] Error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_doctor_blocked_slots(doctor_id: int) -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, doctor_id, blocked_date, start_time, end_time, reason, created_at "
        "FROM dbo.doctor_blocked_slots WHERE doctor_id = ? ORDER BY blocked_date DESC, start_time DESC",
        doctor_id
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    res = []
    for r in rows:
        res.append({
            "id": r[0],
            "doctor_id": r[1],
            "blocked_date": _fmt_date(r[2]),
            "start_time": str(r[3])[:5] if r[3] else "",
            "end_time": str(r[4])[:5] if r[4] else "",
            "reason": r[5] or "",
            "created_at": str(r[6])[:19]
        })
    return res

def add_doctor_blocked_slot(doctor_id: int, blocked_date: str, start_time: str, end_time: str, reason: str, created_by_doctor: bool = False) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1. Validar que no existan citas activas en ese rango
        s_time = start_time + ":00" if len(start_time) == 5 else start_time
        e_time = end_time + ":00" if len(end_time) == 5 else end_time
        
        cursor.execute("""
            SELECT a.id, p.name, a.scheduled_time 
            FROM dbo.appointments a
            JOIN dbo.patients p ON a.patient_id = p.id
            WHERE a.doctor_id = ? 
              AND CAST(a.scheduled_date AS DATE) = CAST(? AS DATE)
              AND a.status IN ('abierta', 'en_curso')
              AND a.scheduled_time >= CAST(? AS TIME)
              AND a.scheduled_time <= CAST(? AS TIME)
        """, doctor_id, blocked_date, s_time, e_time)
        clashes = cursor.fetchall()
        
        if clashes:
            clash_list = [f"{r[1]} a las {str(r[2])[:5]}" for r in clashes]
            clash_str = ", ".join(clash_list)
            raise Exception(f"No se puede bloquear este horario. Existe(n) cita(s) activa(s) programada(s): {clash_str}")
        
        # 2. Insertar el bloqueo
        cursor.execute(
            "INSERT INTO dbo.doctor_blocked_slots (doctor_id, blocked_date, start_time, end_time, reason) "
            "VALUES (?, ?, ?, ?, ?)",
            doctor_id, blocked_date, s_time, e_time, reason
        )
        conn.commit()
        
        # 3. Si fue creado por el doctor, notificar a todas las secretarias
        if created_by_doctor:
            cursor.execute("SELECT full_name FROM dbo.users WHERE id = ?", doctor_id)
            doc_row = cursor.fetchone()
            doc_name = doc_row[0] if doc_row else "Doctor"
            
            cursor.execute("SELECT id FROM dbo.users WHERE role='secretaria' AND is_active=1")
            sec_ids = [r[0] for r in cursor.fetchall()]
            
            msg = f"El Dr. {doc_name} ha bloqueado su horario el {blocked_date} de {start_time} a {end_time}. Razon: {reason}"
            for sec_id in sec_ids:
                cursor.execute(
                    "INSERT INTO dbo.notifications (from_user_id, to_user_id, message, type) "
                    "VALUES (?, ?, ?, ?)",
                    doctor_id, sec_id, msg, "info"
                )
            conn.commit()
            
        return True
    finally:
        cursor.close()
        conn.close()

def delete_doctor_blocked_slot(slot_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM dbo.doctor_blocked_slots WHERE id = ?", slot_id)
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()
