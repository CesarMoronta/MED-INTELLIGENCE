"""
database.py — Capa de acceso a datos para MED-INTELLIGENCE PRO v3.0
Gestiona todas las operaciones con SQL Server via pyodbc.
"""
import os
import json
import pyodbc
import threading
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

# ─── Cadena de conexión ───────────────────────────────────────────────────────
SQLSERVER_CONN = os.environ.get(
    "SQLSERVER_CONN",
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER=ASUS_GAMING_CM;DATABASE=MedIntelligence;Trusted_Connection=yes;Encrypt=no"
)

MAX_LOGIN_ATTEMPTS = 5    # Intentos antes del bloqueo
LOCKOUT_MINUTES    = 15   # Minutos de bloqueo

_local_data = threading.local()

def get_connection() -> pyodbc.Connection:
    conn = pyodbc.connect(SQLSERVER_CONN, autocommit=True)
    if not hasattr(_local_data, "connections"):
        _local_data.connections = []
    _local_data.connections.append(conn)
    return conn

def close_all_thread_connections():
    """
    Cierra de forma segura todas las conexiones de base de datos creadas
    en el hilo actual. Se utiliza en el teardown de Flask para evitar fugas.
    """
    if hasattr(_local_data, "connections"):
        for conn in _local_data.connections:
            try:
                conn.close()
            except Exception:
                pass
        _local_data.connections.clear()


def rows_to_dicts(cursor: pyodbc.Cursor) -> list:
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _fmt_date(val) -> str | None:
    """Convierte objetos datetime/date a string ISO."""
    if val is None:
        return None
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return str(val)


# INICIALIZACIÓN DE LA BASE DE DATOS

def initialize_database(seed_patients=None, default_priors=None, default_conditionals=None):
    """
    Verifica que el schema ya exista (debe ejecutarse database_schema.txt antes).
    Hace el seeding inicial: admin, pacientes de prueba, priors del motor Bayes.
    """
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



# AUTENTICACIÓN Y USUARIOS

def get_user_by_username(username: str) -> dict | None:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT u.id, u.username, u.password_hash, u.role, u.full_name,
                  u.email, u.is_active, u.failed_logins, u.locked_until, u.last_login,
                  d.matricula, d.especialidad, d.telefono, d.hospital, d.id AS doctor_id,
                  u.photo_url, u.subscription_active, u.subscription_id, u.subscription_plan, u.subscription_expires_at,
                  u.cedula
           FROM dbo.users u
           LEFT JOIN dbo.doctors d ON d.user_id = u.id
           WHERE u.username = ?""",
        username
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None

    sub_active = bool(row[16])
    expires_at = row[19] # datetime object
    if not sub_active and expires_at:
        try:
            if expires_at.date() >= datetime.utcnow().date():
                sub_active = True
        except Exception:
            pass

    return {
        "id": row[0], "username": row[1], "password_hash": row[2],
        "role": row[3], "full_name": row[4], "email": row[5],
        "is_active": bool(row[6]), "failed_logins": row[7],
        "locked_until": row[8], "last_login": row[9],
        "matricula": row[10], "especialidad": row[11],
        "telefono": row[12], "hospital": row[13], "doctor_id": row[14],
        "photo_url": row[15], "subscription_active": sub_active,
        "subscription_id": row[17], "subscription_plan": row[18],
        "subscription_expires_at": _fmt_date(row[19]),
        "cedula": row[20]
    }


def get_user_by_id(user_id: int) -> dict | None:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT u.id, u.username, u.password_hash, u.role, u.full_name,
                  u.email, u.is_active, u.failed_logins, u.locked_until, u.last_login,
                  d.matricula, d.especialidad, d.telefono, d.hospital, d.id AS doctor_id,
                  u.photo_url, u.subscription_active, u.subscription_id, u.subscription_plan, u.subscription_expires_at,
                  u.cedula
           FROM dbo.users u
           LEFT JOIN dbo.doctors d ON d.user_id = u.id
           WHERE u.id = ?""",
        user_id
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None

    sub_active = bool(row[16])
    expires_at = row[19] # datetime object
    if not sub_active and expires_at:
        try:
            if expires_at.date() >= datetime.utcnow().date():
                sub_active = True
        except Exception:
            pass

    return {
        "id": row[0], "username": row[1], "password_hash": row[2],
        "role": row[3], "full_name": row[4], "email": row[5],
        "is_active": bool(row[6]), "failed_logins": row[7],
        "locked_until": _fmt_date(row[8]), "last_login": _fmt_date(row[9]),
        "matricula": row[10], "especialidad": row[11],
        "telefono": row[12], "hospital": row[13], "doctor_id": row[14],
        "photo_url": row[15], "subscription_active": sub_active,
        "subscription_id": row[17], "subscription_plan": row[18],
        "subscription_expires_at": _fmt_date(row[19]),
        "cedula": row[20]
    }


def verify_user(username: str, password: str, ip_address: str = None) -> dict | None:
    """
    Verifica credenciales. Registra intento y aplica bloqueo temporal.
    Retorna dict del usuario si es correcto, None si no.
    """
    user = get_user_by_username(username)

    if not user:
        _register_attempt(username, ip_address, False)
        return None

    # Verificar si está bloqueado
    if user.get("locked_until"):
        locked_until = user["locked_until"]
        if isinstance(locked_until, str):
            try:
                from datetime import timezone
                locked_until = datetime.fromisoformat(locked_until)
                if locked_until.tzinfo is None:
                    locked_until = locked_until.replace(tzinfo=timezone.utc)
                from datetime import timezone
                now = datetime.now(timezone.utc)
            except Exception:
                now = datetime.utcnow()
        else:
            now = datetime.utcnow()

        try:
            if locked_until > now:
                return None  # Cuenta bloqueada
        except Exception:
            pass

    if not user.get("is_active"):
        return None

    if not check_password_hash(user["password_hash"], password):
        _register_attempt(username, ip_address, False)
        return None

    _register_attempt(username, ip_address, True)
    return {
        "id": user["id"], "username": user["username"],
        "role": user["role"], "full_name": user.get("full_name"),
        "matricula": user.get("matricula"), "doctor_id": user.get("doctor_id"),
        "photo_url": user.get("photo_url"), "subscription_active": user.get("subscription_active"),
        "cedula": user.get("cedula")
    }


def is_account_locked(username: str) -> bool:
    """Retorna True si la cuenta está bloqueada temporalmente."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT locked_until FROM dbo.users WHERE username = ?", username
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row or row[0] is None:
        return False
    from datetime import timezone
    try:
        locked = row[0]
        now = datetime.now(timezone.utc)
        if locked.tzinfo is None:
            locked = locked.replace(tzinfo=timezone.utc)
        return locked > now
    except Exception:
        return False


def _register_attempt(username: str, ip_address: str, success: bool):
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "EXEC dbo.sp_register_login_attempt ?, ?, ?",
            username, ip_address, 1 if success else 0
        )
        cursor.close()
        conn.close()
    except Exception:
        pass


def create_user(username: str, password: str, role: str,
                full_name: str = None, email: str = None,
                matricula: str = None, especialidad: str = None,
                telefono: str = None, hospital: str = None,
                cedula: str = None, photo_url: str = None) -> dict | None:
    if get_user_by_username(username):
        return None
    pw_hash = generate_password_hash(password)
    conn    = get_connection()
    cursor  = conn.cursor()
    cursor.execute(
        "EXEC dbo.sp_create_user ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
        username, pw_hash, role, full_name, email,
        matricula, especialidad, telefono, hospital,
        cedula, photo_url
    )
    cursor.fetchone()
    cursor.close()
    conn.close()
    return get_user_by_username(username)


def update_user(user_id: int, username: str = None, password: str = None,
                role: str = None, full_name: str = None, email: str = None,
                is_active: bool = None, matricula: str = None,
                especialidad: str = None, telefono: str = None,
                hospital: str = None, cedula: str = None, photo_url: str = None) -> dict | None:
    user = get_user_by_id(user_id)
    if not user:
        return None
    pw_hash = generate_password_hash(password) if password else None
    is_active_val = None
    if is_active is not None:
        is_active_val = 1 if is_active else 0
    conn   = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "EXEC dbo.sp_update_user ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
            user_id, username, pw_hash, role, full_name, email,
            is_active_val, matricula, especialidad, telefono, hospital,
            cedula, photo_url
        )
        cursor.fetchone()
    except pyodbc.Error:
        pass
    finally:
        cursor.close()
        conn.close()
    return get_user_by_id(user_id)


def update_user_subscription(user_id: int, active: bool, sub_id: str = None, plan: str = None, expires_at = None) -> bool:
    """Actualiza la suscripción de un doctor en la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """UPDATE dbo.users
               SET subscription_active = ?,
                   subscription_id = ?,
                   subscription_plan = ?,
                   subscription_expires_at = ?
               WHERE id = ?""",
            1 if active else 0, sub_id, plan, expires_at, user_id
        )
        return True
    except Exception:
        return False
    finally:
        cursor.close()
        conn.close()


def update_user_photo(user_id: int, photo_url: str) -> bool:
    """Actualiza la foto de perfil de un usuario."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE dbo.users SET photo_url = ? WHERE id = ?",
            photo_url, user_id
        )
        return True
    except Exception:
        return False
    finally:
        cursor.close()
        conn.close()


def list_users() -> list:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, username, role, full_name, email, is_active,
                  failed_logins, locked_until, last_login, created_at,
                  matricula, especialidad, telefono, hospital, doctor_id,
                  photo_url, subscription_active, subscription_id, subscription_plan, subscription_expires_at,
                  cedula
           FROM dbo.vw_users
           ORDER BY role DESC, username ASC"""
    )
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["is_active"]   = bool(r.get("is_active", 1))
        r["locked_until"] = _fmt_date(r.get("locked_until"))
        r["last_login"]   = _fmt_date(r.get("last_login"))
        r["created_at"]   = _fmt_date(r.get("created_at"))
        
        sub_active = bool(r.get("subscription_active", 0))
        expires_at = r.get("subscription_expires_at") # datetime object or None
        if not sub_active and expires_at:
            try:
                if expires_at.date() >= datetime.utcnow().date():
                    sub_active = True
            except Exception:
                pass
        r["subscription_active"] = sub_active
        r["subscription_expires_at"] = _fmt_date(r.get("subscription_expires_at"))
    return rows



# PACIENTES

def add_patient(cedula: str, name: str, dob: str, gender: str,
                antecedentes: dict, phone: str = None,
                blood_type: str = None, registered_by: int = None,
                photo_url: str = None) -> bool:
    """Crea un nuevo paciente. Retorna True si tuvo éxito, False si ya existe."""
    conn      = get_connection()
    cursor    = conn.cursor()
    patient_id = None
    try:
        cursor.execute(
            "EXEC dbo.sp_create_patient ?, ?, ?, ?, ?, ?, ?, ?",
            cedula, name, dob, gender, phone, blood_type, registered_by, photo_url
        )
        row        = cursor.fetchone()
        patient_id = int(row[0]) if row else None
    except pyodbc.IntegrityError:
        return False
    finally:
        cursor.close()
        conn.close()

    if not patient_id:
        return False
    _set_patient_antecedents(patient_id, antecedentes)
    return True


def _set_patient_antecedents(patient_id: int, antecedentes: dict):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dbo.patient_antecedents WHERE patient_id = ?", patient_id)
    for ant, val in (antecedentes or {}).items():
        cursor.execute(
            """IF EXISTS (SELECT 1 FROM dbo.patient_antecedents WHERE patient_id=? AND antecedent=?)
                   UPDATE dbo.patient_antecedents SET value=?, updated_at=SYSUTCDATETIME()
                   WHERE patient_id=? AND antecedent=?
               ELSE
                   INSERT INTO dbo.patient_antecedents (patient_id, antecedent, value)
                   VALUES (?, ?, ?)""",
            patient_id, ant, 1 if val else 0, patient_id, ant,
            patient_id, ant, 1 if val else 0
        )
    cursor.close()
    conn.close()


def get_patient(patient_id: int) -> dict | None:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, cedula, name, dob, gender, phone, blood_type, age, antecedentes, created_at, updated_at, photo_url, vital_status, death_date, death_certificate_url, death_notes "
        "FROM dbo.vw_patients WHERE id = ?",
        patient_id
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None
    patient = {
        "id": row[0], "cedula": row[1], "name": row[2],
        "dob": _fmt_date(row[3]), "gender": row[4],
        "phone": row[5], "blood_type": row[6], "age": row[7],
        "antecedentes": {}, "created_at": _fmt_date(row[9]),
        "updated_at": _fmt_date(row[10]), "photo_url": row[11],
        "vital_status": row[12], "death_date": _fmt_date(row[13]),
        "death_certificate_url": row[14], "death_notes": row[15]
    }
    if row[8]:
        parsed = json.loads(row[8])
        patient["antecedentes"] = {item["antecedent"]: bool(item["value"]) for item in parsed}
    return patient


def list_patients(search: str = None, doctor_id: int = None) -> list:
    conn   = get_connection()
    cursor = conn.cursor()
    
    base_query = "SELECT p.id, p.cedula, p.name, p.dob, p.gender, p.phone, p.blood_type, p.age, p.antecedentes, p.photo_url FROM dbo.vw_patients p"
    where_clauses = []
    params = []

    if doctor_id:
        where_clauses.append("(EXISTS (SELECT 1 FROM dbo.appointments a WHERE a.patient_id = p.id AND a.doctor_id = ?) OR EXISTS (SELECT 1 FROM dbo.emergency_visits v WHERE v.patient_id = p.id AND v.doctor_id = ?))")
        params.extend([doctor_id, doctor_id])

    if search:
        like = f"%{search}%"
        where_clauses.append("(p.cedula LIKE ? OR p.name LIKE ?)")
        params.extend([like, like])

    query = base_query
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    query += " ORDER BY p.name ASC"

    cursor.execute(query, *params)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["dob"] = _fmt_date(r.get("dob"))
        if r.get("antecedentes"):
            parsed = json.loads(r["antecedentes"])
            r["antecedentes"] = {item["antecedent"]: bool(item["value"]) for item in parsed}
        else:
            r["antecedentes"] = {}
    return rows


def update_patient(patient_id: int, cedula: str = None, name: str = None,
                   dob: str = None, gender: str = None, phone: str = None,
                   blood_type: str = None, antecedentes: dict = None,
                   photo_url: str = None) -> bool:
    existing = get_patient(patient_id)
    if not existing:
        return False
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "EXEC dbo.sp_update_patient ?, ?, ?, ?, ?, ?, ?, ?",
        patient_id,
        cedula   or None,
        name     or None,
        dob      or None,
        gender   or None,
        phone    or None,
        blood_type or None,
        photo_url or None
    )
    cursor.fetchone()
    cursor.close()
    conn.close()
    if antecedentes is not None:
        _set_patient_antecedents(patient_id, antecedentes)
    return True


def delete_patient(patient_id: int) -> bool:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dbo.patients WHERE id = ?", patient_id)
    rows = cursor.rowcount
    cursor.close()
    conn.close()
    return rows > 0


# VISITAS MÉDICAS

def create_visit(patient_id: int, doctor_id: int, visit_type: str,
                 motivo_consulta: str = None, motivo_emergencia: str = None,
                 doctor_notes: str = None,
                 constantes: dict = None, sintomas: dict = None,
                 appointment_id: int = None) -> int | None:
    """Crea una nueva visita médica y guarda constantes y síntomas."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "EXEC dbo.sp_create_visit ?, ?, ?, ?, ?, ?, ?",
        patient_id, doctor_id, visit_type, motivo_consulta, motivo_emergencia, doctor_notes, appointment_id
    )
    row = cursor.fetchone()
    visit_id = int(row[0]) if row else None
    cursor.close()
    conn.close()

    if not visit_id:
        return None

    # Guardar constantes vitales
    if constantes:
        _save_visit_vitals(visit_id, constantes)

    # Guardar síntomas
    if sintomas:
        _save_visit_symptoms(visit_id, sintomas)

    return visit_id


def _save_visit_vitals(visit_id: int, constantes: dict):
    UNITS = {
        "temperatura": "°C", "spo2": "%", "pas": "mmHg",
        "pad": "mmHg", "fc": "bpm", "fr": "rpm", "edad": "años",
        "peso": "kg", "altura": "cm", "grasa_corporal": "%", "imc": ""
    }
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dbo.visit_vitals WHERE visit_id = ?", visit_id)
    for name, value in constantes.items():
        try:
            val = float(value)
        except (TypeError, ValueError):
            continue
        cursor.execute(
            "INSERT INTO dbo.visit_vitals (visit_id, name, value, unit) VALUES (?, ?, ?, ?)",
            visit_id, name, val, UNITS.get(name)
        )
    cursor.close()
    conn.close()


def _save_visit_symptoms(visit_id: int, sintomas: dict):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dbo.visit_symptoms WHERE visit_id = ?", visit_id)
    for symptom, present in sintomas.items():
        cursor.execute(
            "INSERT INTO dbo.visit_symptoms (visit_id, symptom, present) VALUES (?, ?, ?)",
            visit_id, symptom, 1 if present else 0
        )
    cursor.close()
    conn.close()


def save_visit_tests(visit_id: int, tests: list) -> bool:
    """Guarda los resultados de las pruebas diagnósticas de una visita."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dbo.visit_tests WHERE visit_id = ?", visit_id)
    for t in tests:
        test_name    = t.get("test_name", "")
        was_done     = 1 if t.get("done") else 0
        result       = t.get("result") or None
        result_value = t.get("result_value") or None
        notes        = t.get("notes") or None
        cursor.execute(
            "INSERT INTO dbo.visit_tests (visit_id, test_name, was_done, result, result_value, notes) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            visit_id, test_name, was_done, result, result_value, notes
        )
    cursor.close()
    conn.close()
    return True


def get_visit(visit_id: int) -> dict | None:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, visit_type, motivo_consulta, motivo_emergencia, doctor_notes, visit_date, status,
                  patient_id, patient_cedula, patient_name, patient_dob, patient_gender,
                  doctor_id, doctor_username, doctor_fullname,
                  diagnosis_id, diagnosis_phase, diagnosis_primary, diagnosis_probability,
                  alert_level, alert_color, specialist,
                  appointment_id, parent_appointment_id
           FROM dbo.vw_visits WHERE id = ?""",
        visit_id
    )
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return None

    visit = {
        "id": row[0], "visit_type": row[1], "motivo_consulta": row[2],
        "motivo_emergencia": row[3], "doctor_notes": row[4], "visit_date": _fmt_date(row[5]), "status": row[6],
        "patient_id": row[7], "patient_cedula": row[8], "patient_name": row[9],
        "patient_dob": _fmt_date(row[10]), "patient_gender": row[11],
        "doctor_id": row[12], "doctor_username": row[13], "doctor_fullname": row[14],
        "diagnosis_id": row[15], "diagnosis_phase": row[16],
        "diagnosis_primary": row[17], "diagnosis_probability": row[18],
        "alert_level": row[19], "alert_color": row[20], "specialist": row[21],
        "appointment_id": row[22], "parent_appointment_id": row[23]
    }

    # Constantes vitales
    cursor.execute("SELECT name, value, unit FROM dbo.visit_vitals WHERE visit_id = ?", visit_id)
    visit["constantes"] = {r[0]: float(r[1]) for r in cursor.fetchall()}

    # Síntomas
    cursor.execute("SELECT symptom, present FROM dbo.visit_symptoms WHERE visit_id = ?", visit_id)
    visit["sintomas"] = {r[0]: bool(r[1]) for r in cursor.fetchall()}

    # Pruebas
    cursor.execute(
        "SELECT test_name, was_done, result, result_value, notes FROM dbo.visit_tests WHERE visit_id = ?",
        visit_id
    )
    visit["tests"] = [
        {"test_name": r[0], "done": bool(r[1]), "result": r[2], "result_value": r[3], "notes": r[4]}
        for r in cursor.fetchall()
    ]

    cursor.close()
    conn.close()
    return visit


def list_visits(patient_id: int = None, doctor_id: int = None, limit: int = 100) -> list:
    conn   = get_connection()
    cursor = conn.cursor()

    where_clauses = []
    params = []
    if patient_id:
        where_clauses.append("patient_id = ?")
        params.append(patient_id)
    if doctor_id:
        where_clauses.append("doctor_id = ?")
        params.append(doctor_id)

    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    cursor.execute(
        f"""SELECT TOP ({limit}) id, visit_type, motivo_consulta, motivo_emergencia, doctor_notes, visit_date, status,
                   patient_id, patient_cedula, patient_name, patient_dob, patient_gender,
                   doctor_id, doctor_username, doctor_fullname,
                   diagnosis_id, diagnosis_phase, diagnosis_primary, diagnosis_probability,
                   alert_level, alert_color, specialist
            FROM dbo.vw_visits {where_sql}
            ORDER BY visit_date DESC""",
        *params
    )
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["visit_date"]  = _fmt_date(r.get("visit_date"))
        r["patient_dob"] = _fmt_date(r.get("patient_dob"))
    return rows


# DIAGNÓSTICOS

def save_diagnosis(visit_id: int, phase: str, diagnosis_primary: str,
                   probability: float, alert_level: str, alert_color: str,
                   specialist: str, differentials: dict = None,
                   clinical_report: str = None,
                   is_refuted: bool = False,
                   refutation_reason: str = None,
                   doctor_override_diagnosis: str = None) -> int | None:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "EXEC dbo.sp_save_diagnosis ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
        visit_id, phase, diagnosis_primary, probability,
        alert_level, alert_color, specialist,
        json.dumps(differentials, ensure_ascii=False) if differentials else None,
        clinical_report,
        1 if is_refuted else 0,
        refutation_reason,
        doctor_override_diagnosis
    )
    row = cursor.fetchone()
    diag_id = int(row[0]) if row else None
    cursor.close()
    conn.close()
    return diag_id


def get_clinical_report(diagnosis_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT clinical_report FROM dbo.diagnoses WHERE id = ?", diagnosis_id)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else None


def list_clinical_history(limit: int = 200, doctor_id: int = None, patient_id: int = None, alert_level: str = None) -> list:
    """Lista historial clínico. Si doctor_id, patient_id o alert_level se especifican, filtra por ellos."""
    conn   = get_connection()
    cursor = conn.cursor()
    
    where_clauses = []
    params = []
    if doctor_id:
        where_clauses.append("doctor_id = ?")
        params.append(int(doctor_id))
    if patient_id:
        where_clauses.append("patient_id = ?")
        params.append(int(patient_id))
    if alert_level:
        where_clauses.append("alert_level = ?")
        params.append(alert_level)
        
    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    cursor.execute(
        f"""SELECT TOP ({limit})
               diagnosis_id, visit_id, phase, diagnosis_primary, probability,
               alert_level, alert_color, specialist, diagnosis_date,
               visit_type, motivo_consulta, motivo_emergencia, doctor_notes, visit_date,
               patient_id, patient_cedula, patient_name,
               doctor_id, doctor_username, doctor_fullname
            FROM dbo.vw_clinical_history
            {where_sql}
            ORDER BY diagnosis_date DESC""",
        *params
    )
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["diagnosis_date"] = _fmt_date(r.get("diagnosis_date"))
        r["visit_date"]     = _fmt_date(r.get("visit_date"))
    return rows


# Mantener compatibilidad con código anterior que usa list_records / add_record
def list_records() -> list:
    return list_clinical_history()


def add_record(record: dict) -> bool:
    """
    Compatibilidad con código anterior.
    Crea una visita + diagnóstico final a partir del formato antiguo.
    """
    patient_id     = record.get("patient_id")
    doctor_username = record.get("doctor_username")

    # Obtener doctor_id
    doctor = get_user_by_username(doctor_username) if doctor_username else None
    doctor_id = doctor["id"] if doctor else None

    if not patient_id or not doctor_id:
        return False

    # Crear visita
    visit_id = create_visit(
        patient_id=patient_id,
        doctor_id=doctor_id,
        visit_type="consulta",
        motivo_consulta=record.get("motivo_consulta"),
        doctor_notes=record.get("doctor_notes"),
        constantes=record.get("constantes", {}),
        sintomas={s: True for s in record.get("sintomas", [])}
    )
    if not visit_id:
        return False

    # Guardar diagnóstico
    probabilities = record.get("probabilities", {})
    diag_id = save_diagnosis(
        visit_id=visit_id,
        phase="final",
        diagnosis_primary=record.get("diagnosis", ""),
        probability=float(record.get("probability", 0)),
        alert_level=record.get("alert_level", "Verde"),
        alert_color="#10b981",
        specialist=record.get("specialist", "Medicina General"),
        differentials=probabilities
    )
    return diag_id is not None


# PARÁMETROS DEL MODELO BAYESIANO

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


# PRUEBAS MÉDICAS DISPONIBLES

def get_medical_tests() -> list:
    """Retorna la lista de pruebas médicas que el motor puede procesar."""
    from diagnostic_engine import BayesianDiagnosticSystem
    engine = BayesianDiagnosticSystem()
    tests = []
    for test_name, results in engine.P_test_result.items():
        tests.append({
            "test_name": test_name,
            "possible_results": list(results.keys())
        })
    return tests


# LOGS DE AUDITORÍA

def get_audit_logs(limit: int = 200) -> list:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT TOP ({limit}) id, user_id, username, action, entity, entity_id, "
        f"details, ip_address, logged_at FROM dbo.audit_log ORDER BY logged_at DESC"
    )
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["logged_at"] = _fmt_date(r.get("logged_at"))
    return rows


def log_audit_action(username: str, action: str, entity: str,
                     entity_id: str = None, details: str = None,
                     user_id: int = None, ip_address: str = None):
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO dbo.audit_log (username, action, entity, entity_id, details, ip_address, user_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            username, action, entity, entity_id, details, ip_address, user_id
        )
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error en log_audit_action: {e}")

# SETTINGS

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

# APPOINTMENTS

def list_appointments(doctor_id: int = None, date_filter: str = None) -> list:
    """Lista citas. Filtra por doctor y/o fecha si se especifican."""
    conn   = get_connection()
    cursor = conn.cursor()
    query  = """
        SELECT a.id, a.patient_id, a.doctor_id, a.scheduled_date, a.scheduled_time,
               a.status, a.notes, a.confirmed, a.parent_appointment_id,
               p.name AS patient_name, p.cedula AS patient_cedula,
               u.full_name AS doctor_fullname
        FROM dbo.appointments a
        JOIN dbo.patients p ON a.patient_id = p.id
        JOIN dbo.users    u ON a.doctor_id  = u.id
    """
    where_clauses = []
    params        = []
    if doctor_id:
        where_clauses.append("a.doctor_id = ?")
        params.append(doctor_id)
    if date_filter:
        where_clauses.append("CAST(a.scheduled_date AS DATE) = CAST(? AS DATE)")
        params.append(date_filter)

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    query += " ORDER BY a.scheduled_date ASC, a.scheduled_time ASC"

    cursor.execute(query, *params)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["scheduled_date"] = _fmt_date(r.get("scheduled_date"))
        r["scheduled_time"] = str(r.get("scheduled_time")) if r.get("scheduled_time") else None
        r["confirmed"]      = bool(r.get("confirmed", False))
    return rows

def create_appointment(patient_id: int, doctor_id: int, scheduled_date: str, scheduled_time: str, notes: str = None, parent_appointment_id: int = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO dbo.appointments (patient_id, doctor_id, scheduled_date, scheduled_time, notes, parent_appointment_id) OUTPUT INSERTED.id VALUES (?, ?, ?, ?, ?, ?)",
        patient_id, doctor_id, scheduled_date, scheduled_time, notes, parent_appointment_id
    )
    app_id = int(cursor.fetchone()[0])
    cursor.close()
    conn.close()
    return app_id

def update_appointment_status(appointment_id: int, status: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE dbo.appointments SET status = ?, updated_at = SYSUTCDATETIME() WHERE id = ?", status, appointment_id)
    rows = cursor.rowcount
    cursor.close()
    conn.close()
    return rows > 0

def update_appointment(appointment_id: int, doctor_id: int, scheduled_date: str, scheduled_time: str, status: str, notes: str = None) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE dbo.appointments SET doctor_id = ?, scheduled_date = ?, scheduled_time = ?, status = ?, notes = ?, updated_at = SYSUTCDATETIME() WHERE id = ?",
        doctor_id, scheduled_date, scheduled_time, status, notes, appointment_id
    )
    rows = cursor.rowcount
    cursor.close()
    conn.close()
    return rows > 0

def reschedule_appointment(appointment_id: int, new_date: str, new_time: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE dbo.appointments SET scheduled_date = ?, scheduled_time = ?, updated_at = SYSUTCDATETIME() WHERE id = ?",
        new_date, new_time, appointment_id
    )
    rows = cursor.rowcount
    cursor.close()
    conn.close()
    return rows > 0

# PRESCRIPTIONS

def add_prescription(visit_id: int, medication: str, dosage: str, frequency: str,
                    duration_days: int, quantity: int, notes: str = None) -> int:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO dbo.prescriptions (visit_id, medication, dosage, frequency, "
        "duration_days, quantity, notes) OUTPUT INSERTED.id VALUES (?, ?, ?, ?, ?, ?, ?)",
        visit_id, medication, dosage, frequency, duration_days, quantity, notes
    )
    pid = int(cursor.fetchone()[0])
    cursor.close()
    conn.close()
    return pid


def get_prescriptions_for_visit(visit_id: int) -> list:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, medication, dosage, frequency, duration_days, quantity, notes "
        "FROM dbo.prescriptions WHERE visit_id = ?",
        visit_id
    )
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    return rows


# Alias para uso en pdf_routes
def get_prescriptions(visit_id: int) -> list:
    return get_prescriptions_for_visit(visit_id)


def get_visit_tests(visit_id: int) -> list:
    """Retorna los tests/exámenes de una visita."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT test_name, was_done, result, result_value, notes "
        "FROM dbo.visit_tests WHERE visit_id = ?",
        visit_id
    )
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    return rows


def get_visit_with_details(visit_id: int) -> dict | None:
    """Alias de get_visit para mayor claridad semántica."""
    return get_visit(visit_id)

# DASHBOARD STATS

def get_dashboard_stats(user_id: int = None, role: str = None) -> dict:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT total_patients, total_visits, total_emergencias, total_diagnoses, "
        "active_doctors, total_admins, red_alerts FROM dbo.vw_dashboard_stats"
    )
    row = cursor.fetchone()

    # Diagnóstico más frecuente
    cursor.execute(
        "SELECT TOP 1 diagnosis_primary, COUNT(*) AS cnt "
        "FROM dbo.diagnoses WHERE phase='final' "
        "GROUP BY diagnosis_primary ORDER BY cnt DESC"
    )
    mc_row     = cursor.fetchone()
    most_common = mc_row[0] if mc_row else None

    cursor.close()
    conn.close()

    base = {
        "total_patients":    row[0] if row else 0,
        "total_visits":      row[1] if row else 0,
        "total_emergencias": row[2] if row else 0,
        "total_diagnoses":   row[3] if row else 0,
        "active_doctors":    row[4] if row else 0,
        "total_admins":      row[5] if row else 0,
        "red_alerts":        row[6] if row else 0,
        "most_common":       most_common,
        "is_doctor":         role == "doctor",
    }

    if role == "doctor" and user_id:
        doctor_stats = get_doctor_dashboard_stats(user_id)
        base.update(doctor_stats)

    return base


def get_doctor_dashboard_stats(doctor_id: int) -> dict:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            SUM(CASE WHEN CAST(scheduled_date AS DATE) = CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END),
            SUM(CASE WHEN CAST(scheduled_date AS DATE) = CAST(GETDATE() AS DATE) AND status='abierta' THEN 1 ELSE 0 END),
            SUM(CASE WHEN CAST(scheduled_date AS DATE) = CAST(GETDATE() AS DATE) AND status='completada' THEN 1 ELSE 0 END),
            SUM(CASE WHEN CAST(scheduled_date AS DATE) = CAST(DATEADD(day,1,GETDATE()) AS DATE) THEN 1 ELSE 0 END)
        FROM dbo.appointments
        WHERE doctor_id = ? AND status != 'cancelada'
    """, doctor_id)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return {
        "citas_hoy": row[0] or 0,
        "citas_pendientes": row[1] or 0,
        "citas_hechas": row[2] or 0,
        "citas_manana": row[3] or 0,
    } if row else {"citas_hoy": 0, "citas_pendientes": 0, "citas_hechas": 0, "citas_manana": 0}


# ─── DASHBOARD CHARTS ─────────────────────────────────────────────────────────

def get_dashboard_charts(doctor_id: int = None) -> dict:
    """Retorna datos para todas las gráficas del dashboard admin/doctor."""
    conn   = get_connection()
    cursor = conn.cursor()
    where  = f"AND ev.doctor_id = {int(doctor_id)}" if doctor_id else ""

    # 1. Visitas por semana (últimas 8 semanas)
    cursor.execute(f"""
        SELECT
            DATEPART(YEAR,  visit_date) AS yr,
            DATEPART(WEEK,  visit_date) AS wk,
            COUNT(*) AS total
        FROM dbo.emergency_visits ev
        WHERE visit_date >= DATEADD(WEEK, -8, GETDATE()) {where}
        GROUP BY DATEPART(YEAR, visit_date), DATEPART(WEEK, visit_date)
        ORDER BY yr ASC, wk ASC
    """)
    rows = cursor.fetchall()
    visits_by_week = {
        "labels": [f"Sem {r[1]}" for r in rows],
        "data": [r[2] for r in rows]
    }

    # 2. Diagnósticos más frecuentes (top 8)
    doc_filter = f"AND ev.doctor_id = {int(doctor_id)}" if doctor_id else ""
    cursor.execute(f"""
        SELECT TOP 8 d.diagnosis_primary, COUNT(*) AS cnt
        FROM dbo.diagnoses d
        JOIN dbo.emergency_visits ev ON d.visit_id = ev.id
        WHERE d.phase = 'final' {doc_filter}
        GROUP BY d.diagnosis_primary
        ORDER BY cnt DESC
    """)
    top_diagnoses = [
        {"name": r[0] if r[0] else "Sin diagnóstico", "count": r[1]}
        for r in cursor.fetchall()
    ]

    # 3. Nuevos pacientes por mes (últimos 6 meses)
    cursor.execute("""
        SELECT
            YEAR(created_at)  AS yr,
            MONTH(created_at) AS mo,
            COUNT(*) AS total
        FROM dbo.patients
        WHERE created_at >= DATEADD(MONTH, -6, GETDATE())
        GROUP BY YEAR(created_at), MONTH(created_at)
        ORDER BY yr ASC, mo ASC
    """)
    rows = cursor.fetchall()
    months_map = {1:"Ene", 2:"Feb", 3:"Mar", 4:"Abr", 5:"May", 6:"Jun", 7:"Jul", 8:"Ago", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dic"}
    patients_by_month = {
        "labels": [f"{months_map.get(r[1], '')} {r[0]}" for r in rows],
        "data": [r[2] for r in rows]
    }

    # 4. Emergencias vs Consultas (últimos 6 meses)
    cursor.execute(f"""
        SELECT visit_type, COUNT(*) AS total
        FROM dbo.emergency_visits ev
        WHERE visit_date >= DATEADD(MONTH, -6, GETDATE()) {where}
        GROUP BY visit_type
    """)
    visit_types = {r[0]: r[1] for r in cursor.fetchall()}

    cursor.close()
    conn.close()

    return {
        "visits_by_week":     visits_by_week,
        "top_diagnoses":      top_diagnoses,
        "patients_by_month":  patients_by_month,
        "visit_types":        visit_types,
    }


# ─── SETTINGS AVANZADOS ───────────────────────────────────────────────────────

SETTINGS_KEYS = [
    "clinic_name", "clinic_address", "clinic_phone",
    "clinic_rnc",  "clinic_hours",   "clinic_email",
    "ui_primary_color", "sidebar_order_admin", "sidebar_order_secretaria",
    "sidebar_order_doctor", "allow_doctor_billing", "enable_secretaria_reports",
    "max_login_attempts", "lockout_minutes", "session_timeout_hours"
]


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


# ─── SALA DE ESPERA ───────────────────────────────────────────────────────────

def get_waiting_room(doctor_id: int = None) -> list:
    """Citas del día ordenadas por hora de llegada."""
    conn   = get_connection()
    cursor = conn.cursor()
    where  = "AND a.doctor_id = ?" if doctor_id else ""
    params = [doctor_id] if doctor_id else []
    cursor.execute(
        f"""
        SELECT a.id, a.patient_id, a.scheduled_date, a.scheduled_time, a.status,
               a.notes, a.confirmed,
               p.name AS patient_name, p.cedula AS patient_cedula,
               u.full_name AS doctor_fullname
        FROM dbo.appointments a
        JOIN dbo.patients p ON a.patient_id = p.id
        JOIN dbo.users    u ON a.doctor_id  = u.id
        WHERE CAST(a.scheduled_date AS DATE) = CAST(GETDATE() AS DATE)
          AND a.status NOT IN ('cancelada')
          {where}
        ORDER BY a.scheduled_time ASC
        """,
        *params
    )
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["scheduled_date"] = _fmt_date(r.get("scheduled_date"))
        r["scheduled_time"] = str(r.get("scheduled_time"))[:5] if r.get("scheduled_time") else None
        r["confirmed"]      = bool(r.get("confirmed", False))
    return rows


def mark_patient_arrived(appointment_id: int) -> bool:
    """Registra que el paciente llegó a la sala de espera."""
    conn   = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE dbo.appointments SET status='en_curso', updated_at=SYSUTCDATETIME() "
            "WHERE id=? AND status='abierta'",
            appointment_id
        )
        rows = cursor.rowcount
    finally:
        cursor.close()
        conn.close()
    return rows > 0


def confirm_appointment(appointment_id: int, notes: str = "") -> bool:
    """Confirma la asistencia a la cita."""
    conn   = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE dbo.appointments "
            "SET confirmed=1, notes=COALESCE(NULLIF(?,N''), notes), updated_at=SYSUTCDATETIME() "
            "WHERE id=?",
            notes, appointment_id
        )
        rows = cursor.rowcount
    finally:
        cursor.close()
        conn.close()
    return rows > 0


# ─── PERFIL ENRIQUECIDO DEL PACIENTE ─────────────────────────────────────────

def get_patient_vitals_history(patient_id: int, limit: int = 10) -> list:
    """Devuelve las últimas N visitas con sus constantes vitales."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""SELECT TOP ({limit})
               ev.id AS visit_id, ev.visit_date, ev.visit_type,
               vv.name AS vital_name, vv.value, vv.unit
            FROM dbo.emergency_visits ev
            JOIN dbo.visit_vitals vv ON vv.visit_id = ev.id
            WHERE ev.patient_id = ?
            ORDER BY ev.visit_date DESC""",
        patient_id
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Agrupar por visita
    visits: dict = {}
    for row in rows:
        vid = row[0]
        if vid not in visits:
            visits[vid] = {
                "visit_id":   vid,
                "visit_date": _fmt_date(row[1]),
                "visit_type": row[2],
                "vitals":     {}
            }
        visits[vid]["vitals"][row[3]] = float(row[4])
    return list(visits.values())


def get_active_medications(patient_id: int) -> list:
    """Recetas aún vigentes (fecha visita + duration_days >= hoy)."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.id, p.medication, p.dosage, p.frequency, p.duration_days,
               p.quantity, p.notes, ev.visit_date,
               DATEADD(DAY, p.duration_days, CAST(ev.visit_date AS DATE)) AS expires_on
        FROM dbo.prescriptions p
        JOIN dbo.emergency_visits ev ON ev.id = p.visit_id
        WHERE ev.patient_id = ?
          AND DATEADD(DAY, p.duration_days, CAST(ev.visit_date AS DATE)) >= CAST(GETDATE() AS DATE)
        ORDER BY ev.visit_date DESC
        """,
        patient_id
    )
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["visit_date"]  = _fmt_date(r.get("visit_date"))
        r["expires_on"]  = _fmt_date(r.get("expires_on"))
    return rows


def get_patient_red_alerts(patient_id: int) -> list:
    """Diagnósticos en alerta Roja anteriores del paciente."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT d.id, d.diagnosis_primary, d.probability, d.alert_level,
               d.alert_color, d.specialist, d.created_at, ev.visit_date,
               u.full_name AS doctor_fullname
        FROM dbo.diagnoses d
        JOIN dbo.emergency_visits ev ON ev.id = d.visit_id
        JOIN dbo.users u ON u.id = ev.doctor_id
        WHERE ev.patient_id = ? AND d.alert_level = 'Rojo' AND d.phase = 'final'
        ORDER BY d.created_at DESC
        """,
        patient_id
    )
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["created_at"] = _fmt_date(r.get("created_at"))
        r["visit_date"] = _fmt_date(r.get("visit_date"))
    return rows


# ─── DOCUMENTOS DEL PACIENTE ──────────────────────────────────────────────────

def list_patient_documents(patient_id: int) -> list:
    conn   = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT d.id, d.patient_id, d.filename, d.original_name, d.file_type,
                      d.file_size, d.file_path, d.uploaded_at,
                      u.full_name AS uploaded_by_name
               FROM dbo.patient_documents d
               LEFT JOIN dbo.users u ON u.id = d.uploaded_by
               WHERE d.patient_id = ?
               ORDER BY d.uploaded_at DESC""",
            patient_id
        )
        rows = rows_to_dicts(cursor)
    except Exception:
        rows = []
    finally:
        cursor.close()
        conn.close()
    for r in rows:
        r["uploaded_at"] = _fmt_date(r.get("uploaded_at"))
    return rows


def add_patient_document(patient_id: int, filename: str, original_name: str,
                         file_type: str, file_size: int,
                         file_path: str, uploaded_by: int) -> int:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO dbo.patient_documents "
        "(patient_id, filename, original_name, file_type, file_size, file_path, uploaded_by) "
        "OUTPUT INSERTED.id VALUES (?, ?, ?, ?, ?, ?, ?)",
        patient_id, filename, original_name, file_type, file_size, file_path, uploaded_by
    )
    doc_id = int(cursor.fetchone()[0])
    cursor.close()
    conn.close()
    return doc_id


def get_patient_document(doc_id: int) -> dict | None:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, patient_id, filename, original_name, file_type, file_size, file_path, uploaded_at "
        "FROM dbo.patient_documents WHERE id = ?",
        doc_id
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0], "patient_id": row[1], "filename": row[2],
        "original_name": row[3], "file_type": row[4],
        "file_size": row[5], "file_path": row[6],
        "uploaded_at": _fmt_date(row[7])
    }


def delete_patient_document(doc_id: int) -> bool:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dbo.patient_documents WHERE id = ?", doc_id)
    rows   = cursor.rowcount
    cursor.close()
    conn.close()
    return rows > 0


# ─── NOTIFICACIONES / CHAT INTERNO ───────────────────────────────────────────

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


def list_pending_bills() -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ev.id AS visit_id, ev.visit_date, p.name AS patient_name, p.cedula AS patient_cedula,
               u.full_name AS doctor_fullname, p.id AS patient_id
        FROM dbo.emergency_visits ev
        INNER JOIN dbo.patients p ON ev.patient_id = p.id
        INNER JOIN dbo.users u ON ev.doctor_id = u.id
        LEFT JOIN dbo.appointments app ON ev.appointment_id = app.id
        WHERE ev.status = 'cerrada' AND ev.visit_type = 'consulta'
          AND (
              SELECT COALESCE(SUM(total), 0)
              FROM dbo.invoices
              WHERE visit_id = ev.id
          ) = 0
          AND (app.parent_appointment_id IS NULL OR ev.appointment_id IS NULL)
        ORDER BY ev.visit_date DESC
    """)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["visit_date"] = _fmt_date(r.get("visit_date"))
    return rows


def get_patient_billing_info(patient_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT patient_id, rnc, razon_social, correo
        FROM dbo.patient_billing_info
        WHERE patient_id = ?
    """, patient_id)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None
    return {
        "patient_id": row[0],
        "rnc": row[1],
        "razon_social": row[2],
        "correo": row[3]
    }


def save_patient_billing_info(patient_id: int, rnc: str, razon_social: str, correo: str | None) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            IF EXISTS (SELECT 1 FROM dbo.patient_billing_info WHERE patient_id = ?)
                UPDATE dbo.patient_billing_info
                SET rnc = ?, razon_social = ?, correo = ?, updated_at = SYSUTCDATETIME()
                WHERE patient_id = ?
            ELSE
                INSERT INTO dbo.patient_billing_info (patient_id, rnc, razon_social, correo)
                VALUES (?, ?, ?, ?)
        """, patient_id, rnc, razon_social, correo, patient_id,
             patient_id, rnc, razon_social, correo)
        return True
    except Exception as e:
        print(f"Error guardando informacion de facturacion del paciente: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def create_invoice(visit_id: int | None, user_id: int | None, invoice_type: str,
                   amount: float, itbis: float, total: float, payment_method: str,
                   ecf_id: str | None, encf: str | None, estado: str, track_id: str | None,
                   codigo_seguridad: str | None, dgii_url: str | None, xml_url: str | None,
                   tipo_ecf: str | None = None, amount_paid: float = None, balance_due: float = None, due_date: str = None) -> int | None:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if amount_paid is None:
            amount_paid = total
        if balance_due is None:
            balance_due = 0.0
            
        cursor.execute("""
            INSERT INTO dbo.invoices (visit_id, user_id, invoice_type, amount, itbis, total,
                                      payment_method, ecf_id, encf, estado, track_id,
                                      codigo_seguridad, dgii_url, xml_url, tipo_ecf, amount_paid, balance_due, due_date)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, visit_id, user_id, invoice_type, amount, itbis, total,
             payment_method, ecf_id, encf, estado, track_id,
             codigo_seguridad, dgii_url, xml_url, tipo_ecf, amount_paid, balance_due, due_date)
        row = cursor.fetchone()
        invoice_id = int(row[0]) if row else None
        return invoice_id
    except Exception as e:
        print(f"Error insertando factura: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def list_invoices() -> list:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.visit_id, i.user_id, i.invoice_type, i.amount, i.itbis, i.total,
               i.payment_method, i.ecf_id, i.encf, i.estado, i.track_id, i.codigo_seguridad,
               i.dgii_url, i.xml_url, i.created_at, i.tipo_ecf, i.amount_paid, i.balance_due, i.due_date,
               p.name AS patient_name, p.cedula AS patient_cedula, p.id AS patient_id,
               u.full_name AS doctor_fullname,
               CASE 
                   WHEN i.invoice_type <> 'nota_credito' AND EXISTS (
                       SELECT 1 FROM dbo.invoices cn 
                       WHERE cn.visit_id = i.visit_id 
                         AND cn.invoice_type = 'nota_credito' 
                         AND cn.created_at > i.created_at
                   ) THEN 1 
                   ELSE 0 
               END AS is_cancelled
        FROM dbo.invoices i
        LEFT JOIN dbo.emergency_visits ev ON i.visit_id = ev.id
        LEFT JOIN dbo.patients p ON ev.patient_id = p.id
        LEFT JOIN dbo.users u ON (ev.doctor_id = u.id OR i.user_id = u.id)
        ORDER BY i.created_at DESC
    """)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["created_at"] = _fmt_date(r.get("created_at"))
        r["amount"] = float(r["amount"])
        r["itbis"] = float(r["itbis"])
        r["total"] = float(r["total"])
        r["amount_paid"] = float(r["amount_paid"]) if r.get("amount_paid") is not None else 0.0
        r["balance_due"] = float(r["balance_due"]) if r.get("balance_due") is not None else 0.0
        r["due_date"] = _fmt_date(r.get("due_date"))
        r["is_cancelled"] = bool(r.get("is_cancelled", 0))
    return rows


def get_invoice_by_id(invoice_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.visit_id, i.user_id, i.invoice_type, i.amount, i.itbis, i.total,
               i.payment_method, i.ecf_id, i.encf, i.estado, i.track_id, i.codigo_seguridad,
               i.dgii_url, i.xml_url, i.created_at, i.tipo_ecf, i.amount_paid, i.balance_due, i.due_date,
               p.name AS patient_name, p.cedula AS patient_cedula, p.id AS patient_id,
               u.full_name AS doctor_fullname
        FROM dbo.invoices i
        LEFT JOIN dbo.emergency_visits ev ON i.visit_id = ev.id
        LEFT JOIN dbo.patients p ON ev.patient_id = p.id
        LEFT JOIN dbo.users u ON (ev.doctor_id = u.id OR i.user_id = u.id)
        WHERE i.id = ?
    """, invoice_id)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0], "visit_id": row[1], "user_id": row[2], "invoice_type": row[3],
        "amount": float(row[4]) if row[4] is not None else 0.0,
        "itbis": float(row[5]) if row[5] is not None else 0.0,
        "total": float(row[6]) if row[6] is not None else 0.0,
        "payment_method": row[7], "ecf_id": row[8], "encf": row[9], "estado": row[10],
        "track_id": row[11], "codigo_seguridad": row[12], "dgii_url": row[13],
        "xml_url": row[14], "created_at": _fmt_date(row[15]), "tipo_ecf": row[16],
        "amount_paid": float(row[17]) if row[17] is not None else 0.0,
        "balance_due": float(row[18]) if row[18] is not None else 0.0,
        "due_date": _fmt_date(row[19]),
        "patient_name": row[20], "patient_cedula": row[21], "patient_id": row[22],
        "doctor_fullname": row[23]
    }


# =============================================================================
# REPORTES — Funciones de acceso a datos para el módulo reports.py
# =============================================================================

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


def get_report_patient(patient_id: int, doctor_id: int = None) -> list:
    """Historial clínico completo de un paciente. Doctor solo ve si atendió al paciente."""
    conn = get_connection()
    cursor = conn.cursor()
    if doctor_id is not None:
        cursor.execute("""
            SELECT diagnosis_id, visit_id, phase, diagnosis_primary, probability,
                   alert_level, alert_color, specialist, diagnosis_date,
                   visit_type, motivo_consulta, motivo_emergencia, doctor_notes,
                   visit_date, patient_id, patient_cedula, patient_name,
                   doctor_id, doctor_username, doctor_fullname
            FROM dbo.vw_clinical_history
            WHERE patient_id = ? AND doctor_id = ?
            ORDER BY diagnosis_date DESC
        """, patient_id, doctor_id)
    else:
        cursor.execute("""
            SELECT diagnosis_id, visit_id, phase, diagnosis_primary, probability,
                   alert_level, alert_color, specialist, diagnosis_date,
                   visit_type, motivo_consulta, motivo_emergencia, doctor_notes,
                   visit_date, patient_id, patient_cedula, patient_name,
                   doctor_id, doctor_username, doctor_fullname
            FROM dbo.vw_clinical_history
            WHERE patient_id = ?
            ORDER BY diagnosis_date DESC
        """, patient_id)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["diagnosis_date"] = _fmt_date(r.get("diagnosis_date"))
        r["visit_date"] = _fmt_date(r.get("visit_date"))
        r["probability"] = float(r["probability"]) if r.get("probability") is not None else None
    return rows


def get_report_visits(doctor_id: int = None, date_from: str = None,
                      date_to: str = None, visit_type: str = None) -> list:
    """Lista de visitas filtrable por doctor, rango de fechas y tipo."""
    conn = get_connection()
    cursor = conn.cursor()
    params = []
    conditions = []

    if doctor_id is not None:
        conditions.append("doctor_id = ?")
        params.append(doctor_id)
    if date_from:
        conditions.append("CAST(visit_date AS DATE) >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("CAST(visit_date AS DATE) <= ?")
        params.append(date_to)
    if visit_type:
        conditions.append("visit_type = ?")
        params.append(visit_type)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    cursor.execute(f"""
        SELECT id, visit_type, motivo_consulta, motivo_emergencia, doctor_notes,
               visit_date, status, created_at,
               patient_id, patient_cedula, patient_name, patient_dob, patient_gender,
               doctor_id, doctor_username, doctor_fullname,
               diagnosis_id, diagnosis_phase, diagnosis_primary,
               diagnosis_probability, alert_level, alert_color, specialist
        FROM dbo.vw_visits
        {where}
        ORDER BY visit_date DESC
    """, *params)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["visit_date"] = _fmt_date(r.get("visit_date"))
        r["created_at"] = _fmt_date(r.get("created_at"))
        r["patient_dob"] = _fmt_date(r.get("patient_dob"))
        r["diagnosis_probability"] = float(r["diagnosis_probability"]) if r.get("diagnosis_probability") is not None else None
    return rows


def get_report_waiting_time(doctor_id: int = None, date_from: str = None,
                            date_to: str = None) -> list:
    """Tiempos de espera por cita (desde vw_reports_waiting_time)."""
    conn = get_connection()
    cursor = conn.cursor()
    params = []
    conditions = []

    if doctor_id is not None:
        conditions.append("doctor_id = ?")
        params.append(doctor_id)
    if date_from:
        conditions.append("scheduled_date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("scheduled_date <= ?")
        params.append(date_to)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    cursor.execute(f"""
        SELECT appointment_id, patient_id, patient_name,
               doctor_id, doctor_fullname,
               scheduled_date, scheduled_time, actual_arrival,
               wait_minutes, appointment_status
        FROM dbo.vw_reports_waiting_time
        {where}
        ORDER BY scheduled_date DESC
    """, *params)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["scheduled_date"] = _fmt_date(r.get("scheduled_date"))
        r["actual_arrival"] = _fmt_date(r.get("actual_arrival"))
        r["wait_minutes"] = int(r["wait_minutes"]) if r.get("wait_minutes") is not None else None
    return rows


def get_report_diagnoses_summary(doctor_id: int = None, date_from: str = None,
                                 date_to: str = None) -> list:
    """Resumen agrupado de diagnósticos por enfermedad y nivel de alerta."""
    conn = get_connection()
    cursor = conn.cursor()
    params = []
    conditions = ["phase = 'final'"]

    if doctor_id is not None:
        conditions.append("doctor_id = ?")
        params.append(doctor_id)
    if date_from:
        conditions.append("CAST(diagnosis_date AS DATE) >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("CAST(diagnosis_date AS DATE) <= ?")
        params.append(date_to)

    where = "WHERE " + " AND ".join(conditions)
    cursor.execute(f"""
        SELECT diagnosis_primary, alert_level,
               COUNT(*)        AS total,
               AVG(probability) AS avg_probability,
               MAX(probability) AS max_probability,
               MIN(probability) AS min_probability
        FROM dbo.vw_clinical_history
        {where}
        GROUP BY diagnosis_primary, alert_level
        ORDER BY total DESC
    """, *params)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["total"] = int(r["total"])
        r["avg_probability"] = round(float(r["avg_probability"]), 4) if r.get("avg_probability") is not None else None
        r["max_probability"] = round(float(r["max_probability"]), 4) if r.get("max_probability") is not None else None
        r["min_probability"] = round(float(r["min_probability"]), 4) if r.get("min_probability") is not None else None
    return rows


def get_report_model_performance(doctor_id: int = None, date_from: str = None,
                                 date_to: str = None) -> dict:
    """Métricas de rendimiento del motor bayesiano (refutaciones, alertas, probabilidades)."""
    conn = get_connection()
    cursor = conn.cursor()
    params = []
    conditions = ["d.phase = 'final'"]

    if doctor_id is not None:
        conditions.append("ev.doctor_id = ?")
        params.append(doctor_id)
    if date_from:
        conditions.append("CAST(d.created_at AS DATE) >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("CAST(d.created_at AS DATE) <= ?")
        params.append(date_to)

    where = "WHERE " + " AND ".join(conditions)
    cursor.execute(f"""
        SELECT
            COUNT(*)                                                          AS total_diagnoses,
            SUM(CASE WHEN d.is_refuted = 1 THEN 1 ELSE 0 END)               AS total_refuted,
            AVG(d.probability)                                                AS avg_probability,
            SUM(CASE WHEN d.alert_level = 'Rojo'    THEN 1 ELSE 0 END)      AS red_alerts,
            SUM(CASE WHEN d.alert_level = 'Amarillo' THEN 1 ELSE 0 END)     AS yellow_alerts,
            SUM(CASE WHEN d.alert_level = 'Verde'    THEN 1 ELSE 0 END)     AS green_alerts,
            SUM(CASE WHEN d.doctor_override_diagnosis IS NOT NULL THEN 1 ELSE 0 END) AS overridden
        FROM dbo.diagnoses d
        JOIN dbo.emergency_visits ev ON d.visit_id = ev.id
        {where}
    """, *params)
    row = cursor.fetchone()

    # Top 5 diagnósticos más frecuentes
    cursor.execute(f"""
        SELECT TOP 5 d.diagnosis_primary, COUNT(*) AS total
        FROM dbo.diagnoses d
        JOIN dbo.emergency_visits ev ON d.visit_id = ev.id
        {where}
        GROUP BY d.diagnosis_primary
        ORDER BY total DESC
    """, *params)
    top_diagnoses = [{"diagnosis": r[0], "total": r[1]} for r in cursor.fetchall()]

    cursor.close()
    conn.close()

    if not row:
        return {}

    total = row[0] or 0
    return {
        "total_diagnoses":  total,
        "total_refuted":    int(row[1] or 0),
        "refutation_rate":  round((row[1] or 0) / total, 4) if total else 0,
        "avg_probability":  round(float(row[2]), 4) if row[2] is not None else None,
        "red_alerts":       int(row[3] or 0),
        "yellow_alerts":    int(row[4] or 0),
        "green_alerts":     int(row[5] or 0),
        "overridden":       int(row[6] or 0),
        "top_diagnoses":    top_diagnoses,
    }


def get_report_doctor_activity(date_from: str = None, date_to: str = None) -> list:
    """Actividad por doctor: visitas, emergencias, diagnósticos. Solo para admin."""
    conn = get_connection()
    cursor = conn.cursor()
    params = []
    conditions = []

    if date_from:
        conditions.append("CAST(v.visit_date AS DATE) >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("CAST(v.visit_date AS DATE) <= ?")
        params.append(date_to)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    cursor.execute(f"""
        SELECT
            v.doctor_id,
            v.doctor_fullname,
            u.especialidad,
            COUNT(*)                                                         AS total_visits,
            SUM(CASE WHEN v.visit_type = 'emergencia' THEN 1 ELSE 0 END)    AS total_emergencias,
            SUM(CASE WHEN v.visit_type = 'consulta'   THEN 1 ELSE 0 END)    AS total_consultas,
            SUM(CASE WHEN v.diagnosis_id IS NOT NULL  THEN 1 ELSE 0 END)    AS visits_with_diagnosis,
            SUM(CASE WHEN v.alert_level  = 'Rojo'     THEN 1 ELSE 0 END)    AS red_alerts
        FROM dbo.vw_visits v
        LEFT JOIN dbo.vw_users u ON u.id = v.doctor_id
        {where}
        GROUP BY v.doctor_id, v.doctor_fullname, u.especialidad
        ORDER BY total_visits DESC
    """, *params)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["total_visits"] = int(r["total_visits"])
        r["total_emergencias"] = int(r["total_emergencias"])
        r["total_consultas"] = int(r["total_consultas"])
        r["visits_with_diagnosis"] = int(r["visits_with_diagnosis"])
        r["red_alerts"] = int(r["red_alerts"])
    return rows


def get_report_billing(date_from: str = None, date_to: str = None,
                       invoice_type: str = None, doctor_id: int = None) -> dict:
    """Reporte de facturación con totales globales y listado detallado."""
    conn = get_connection()
    cursor = conn.cursor()
    params = []
    conditions = []

    if date_from:
        conditions.append("CAST(i.created_at AS DATE) >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("CAST(i.created_at AS DATE) <= ?")
        params.append(date_to)
    if invoice_type:
        conditions.append("i.invoice_type = ?")
        params.append(invoice_type)
    if doctor_id:
        # Nota: asume que 'ev' será un alias disponible en el JOIN
        conditions.append("ev.doctor_id = ?")
        params.append(doctor_id)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    # Totales globales
    cursor.execute(f"""
        SELECT
            COUNT(*)                                                                    AS total_invoices,
            COALESCE(SUM(CASE WHEN i.total > 0 THEN i.total ELSE 0 END), 0)           AS total_ingresos,
            COALESCE(SUM(CASE WHEN i.total < 0 THEN ABS(i.total) ELSE 0 END), 0)      AS total_creditos,
            COALESCE(SUM(CASE WHEN i.invoice_type = 'consulta' THEN i.total ELSE 0 END), 0) AS ingresos_consultas,
            COALESCE(SUM(CASE WHEN i.invoice_type = 'suscripcion' THEN i.total ELSE 0 END), 0) AS ingresos_suscripciones,
            COALESCE(SUM(i.itbis), 0)                                                  AS total_itbis
        FROM dbo.invoices i
        LEFT JOIN dbo.emergency_visits ev ON i.visit_id = ev.id
        {where}
    """, *params)
    summary_row = cursor.fetchone()

    # Detalle línea a línea
    cursor.execute(f"""
        SELECT i.id, i.visit_id, i.invoice_type, i.amount, i.itbis, i.total,
               i.payment_method, i.encf, i.estado, i.tipo_ecf, i.created_at,
               p.name AS patient_name, p.cedula AS patient_cedula,
               u.full_name AS doctor_fullname
        FROM dbo.invoices i
        LEFT JOIN dbo.emergency_visits ev ON i.visit_id = ev.id
        LEFT JOIN dbo.patients p ON ev.patient_id = p.id
        LEFT JOIN dbo.users u ON (ev.doctor_id = u.id OR i.user_id = u.id)
        {where}
        ORDER BY i.created_at DESC
    """, *params)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()

    for r in rows:
        r["created_at"] = _fmt_date(r.get("created_at"))
        r["amount"] = float(r["amount"]) if r.get("amount") is not None else 0.0
        r["itbis"] = float(r["itbis"]) if r.get("itbis") is not None else 0.0
        r["total"] = float(r["total"]) if r.get("total") is not None else 0.0

    return {
        "summary": {
            "total_invoices":        int(summary_row[0] or 0),
            "total_ingresos":        float(summary_row[1] or 0),
            "total_creditos":        float(summary_row[2] or 0),
            "ingresos_consultas":    float(summary_row[3] or 0),
            "ingresos_suscripciones": float(summary_row[4] or 0),
            "total_itbis":           float(summary_row[5] or 0),
        },
        "invoices": rows,
    }


def get_report_audit(limit: int = 500, date_from: str = None,
                     date_to: str = None, action: str = None,
                     entity: str = None) -> list:
    """Registro de auditoría filtrable. Extiende get_audit_logs() con filtros."""
    conn = get_connection()
    cursor = conn.cursor()
    params = []
    conditions = []

    if date_from:
        conditions.append("CAST(logged_at AS DATE) >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("CAST(logged_at AS DATE) <= ?")
        params.append(date_to)
    if action:
        conditions.append("action = ?")
        params.append(action)
    if entity:
        conditions.append("entity = ?")
        params.append(entity)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    cursor.execute(f"""
        SELECT TOP ({int(limit)})
            id, user_id, username, action, entity, entity_id,
            details, ip_address, logged_at
        FROM dbo.audit_log
        {where}
        ORDER BY logged_at DESC
    """, *params)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["logged_at"] = _fmt_date(r.get("logged_at"))
    return rows


def get_report_waiting_time(doctor_id: int = None,
                            date_from: str = None,
                            date_to: str = None) -> list:
    """
    Tiempos de espera entre la hora agendada y la llegada real del paciente.
    Solo incluye citas que tengan una visita vinculada (appointment_id en
    emergency_visits). Las citas sin visita se omiten porque no hay hora real.

    Retorna: appointment_id, patient_name, patient_cedula, doctor_fullname,
             scheduled_date, scheduled_time, actual_arrival, wait_minutes,
             visit_type, visit_status.
    wait_minutes es negativo si el paciente llegó antes de la cita.
    """
    conn = get_connection()
    cursor = conn.cursor()
    params = []
    conditions = ["ev.appointment_id IS NOT NULL"]

    if doctor_id:
        conditions.append("a.doctor_id = ?")
        params.append(doctor_id)
    if date_from:
        conditions.append("CAST(a.scheduled_date AS DATE) >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("CAST(a.scheduled_date AS DATE) <= ?")
        params.append(date_to)

    where = "WHERE " + " AND ".join(conditions)

    cursor.execute(f"""
        SELECT
            a.id                                                    AS appointment_id,
            p.name                                                  AS patient_name,
            p.cedula                                                AS patient_cedula,
            u.full_name                                             AS doctor_fullname,
            CONVERT(VARCHAR(10), a.scheduled_date, 23)              AS scheduled_date,
            CONVERT(VARCHAR(5),  a.scheduled_time, 108)             AS scheduled_time,
            CONVERT(VARCHAR(19), ev.visit_date, 120)                AS actual_arrival,
            DATEDIFF(
                MINUTE,
                CAST(
                    CONVERT(VARCHAR(10), a.scheduled_date, 23) + ' '
                    + CONVERT(VARCHAR(8), a.scheduled_time, 108)
                AS DATETIME),
                CAST(ev.visit_date AS DATETIME)
            )                                                       AS wait_minutes,
            ev.visit_type,
            ev.status                                               AS visit_status,
            a.status                                                AS appointment_status
        FROM dbo.appointments      a
        INNER JOIN dbo.emergency_visits ev ON ev.appointment_id = a.id
        INNER JOIN dbo.patients         p  ON p.id  = a.patient_id
        INNER JOIN dbo.users            u  ON u.id  = a.doctor_id
        {where}
        ORDER BY a.scheduled_date DESC, a.scheduled_time DESC
    """, *params)

    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()

    for r in rows:
        if r.get("wait_minutes") is not None:
            r["wait_minutes"] = int(r["wait_minutes"])

    return rows


def get_report_prescriptions(doctor_id: int = None, limit: int = 100) -> list:
    """Obtiene las recetas recientes emitidas, filtrable por doctor."""
    conn = get_connection()
    cursor = conn.cursor()
    params = []
    where_sql = ""
    if doctor_id is not None:
        where_sql = "WHERE ev.doctor_id = ?"
        params.append(doctor_id)
    
    cursor.execute(f"""
        SELECT TOP ({limit})
            pr.id, pr.visit_id, pr.medication, pr.dosage, pr.frequency,
            pr.duration_days, pr.quantity, pr.notes, pr.created_at,
            ev.patient_id, p.name AS patient_name, p.cedula AS patient_cedula
        FROM dbo.prescriptions pr
        INNER JOIN dbo.emergency_visits ev ON pr.visit_id = ev.id
        INNER JOIN dbo.patients p ON ev.patient_id = p.id
        {where_sql}
        ORDER BY pr.created_at DESC
    """, *params)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["created_at"] = _fmt_date(r.get("created_at"))
    return rows


def get_report_recurrent_patients(doctor_id: int = None, min_visits: int = 2) -> list:
    """Obtiene pacientes con múltiples visitas, opcionalmente filtrados por doctor."""
    conn = get_connection()
    cursor = conn.cursor()
    params = []
    where_sql = ""
    if doctor_id is not None:
        where_sql = "WHERE ev.doctor_id = ?"
        params.append(doctor_id)
        
    cursor.execute(f"""
        SELECT 
            ev.patient_id, p.name AS patient_name, p.cedula AS patient_cedula, p.phone,
            COUNT(ev.id) AS total_visits,
            MAX(ev.visit_date) AS last_visit_date,
            MIN(ev.visit_date) AS first_visit_date
        FROM dbo.emergency_visits ev
        INNER JOIN dbo.patients p ON ev.patient_id = p.id
        {where_sql}
        GROUP BY ev.patient_id, p.name, p.cedula, p.phone
        HAVING COUNT(ev.id) >= {min_visits}
        ORDER BY total_visits DESC
    """, *params)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["last_visit_date"] = _fmt_date(r.get("last_visit_date"))
        r["first_visit_date"] = _fmt_date(r.get("first_visit_date"))
    return rows


def get_report_ai_comparison(doctor_id: int = None) -> list:
    """Detalle de diagnósticos finales donde el médico refutó a la IA."""
    conn = get_connection()
    cursor = conn.cursor()
    params = []
    where_sql = "WHERE d.phase = 'final' AND d.is_refuted = 1"
    if doctor_id is not None:
        where_sql += " AND ev.doctor_id = ?"
        params.append(doctor_id)
        
    cursor.execute(f"""
        SELECT 
            d.id AS diagnosis_id, d.visit_id, d.diagnosis_primary AS final_diagnosis,
            d.doctor_override_diagnosis, d.refutation_reason, d.created_at,
            ev.patient_id, p.name AS patient_name
        FROM dbo.diagnoses d
        INNER JOIN dbo.emergency_visits ev ON d.visit_id = ev.id
        INNER JOIN dbo.patients p ON ev.patient_id = p.id
        {where_sql}
        ORDER BY d.created_at DESC
    """, *params)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["created_at"] = _fmt_date(r.get("created_at"))
    return rows

def mark_patient_deceased(patient_id: int, death_date: str, cert_path: str, notes: str, doctor_id: int, doctor_username: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE dbo.patients SET vital_status = 'Fallecido', death_date = ?, death_certificate_url = ?, death_notes = ?, updated_at = SYSUTCDATETIME() WHERE id = ?",
            death_date, cert_path, notes, patient_id
        )
        if cursor.rowcount > 0:
            cursor.execute(
                "INSERT INTO dbo.audit_log (username, action, entity, entity_id, details, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                doctor_username, 'MARCAR_FALLECIDO', 'Patient', str(patient_id), f"Fallecimiento registrado: {death_date}", doctor_id
            )
            return True
        return False
    except Exception as e:
        print(f"Error marking patient deceased: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_patient_account_statement(patient_id: int, doctor_id: int) -> dict | None:
    # Validate access
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM dbo.appointments a WHERE a.patient_id = ? AND a.doctor_id = ?
        UNION
        SELECT 1 FROM dbo.emergency_visits ev WHERE ev.patient_id = ? AND ev.doctor_id = ?
    """, patient_id, doctor_id, patient_id, doctor_id)
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return None # Access denied or no records

    # Access granted, fetch invoices
    cursor.execute("""
        SELECT i.id, i.created_at, i.invoice_type, i.total, i.amount_paid, i.balance_due, i.estado, i.due_date
        FROM dbo.invoices i
        JOIN dbo.emergency_visits ev ON ev.id = i.visit_id
        WHERE ev.patient_id = ?
        ORDER BY i.created_at DESC
    """, patient_id)
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    
    total_balance = 0.0
    for r in rows:
        r["created_at"] = _fmt_date(r.get("created_at"))
        r["due_date"] = _fmt_date(r.get("due_date"))
        r["total"] = float(r["total"])
        r["amount_paid"] = float(r["amount_paid"])
        r["balance_due"] = float(r["balance_due"])
        if r["invoice_type"] != 'nota_credito' and r["estado"] != 'Cancelada':
            total_balance += r["balance_due"]
            
    return {
        "total_balance": total_balance,
        "invoices": rows
    }
