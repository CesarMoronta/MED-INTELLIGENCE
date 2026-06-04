"""
database.py — Capa de acceso a datos para MED-INTELLIGENCE PRO v3.0
Gestiona todas las operaciones con SQL Server via pyodbc.
"""
import os
import json
import pyodbc
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash

# ─── Cadena de conexión ───────────────────────────────────────────────────────
SQLSERVER_CONN = os.environ.get(
    "SQLSERVER_CONN",
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER=ASUS_GAMING_CM;"
    "DATABASE=MedIntelligence;Trusted_Connection=yes;Encrypt=no"
)

MAX_LOGIN_ATTEMPTS = 5    # Intentos antes del bloqueo
LOCKOUT_MINUTES    = 15   # Minutos de bloqueo


def get_connection() -> pyodbc.Connection:
    return pyodbc.connect(SQLSERVER_CONN, autocommit=True)


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


# AUTENTICACIÓN Y USUARIOS

def get_user_by_username(username: str) -> dict | None:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT u.id, u.username, u.password_hash, u.role, u.full_name,
                  u.email, u.is_active, u.failed_logins, u.locked_until, u.last_login,
                  d.matricula, d.especialidad, d.telefono, d.hospital, d.id AS doctor_id
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
    return {
        "id": row[0], "username": row[1], "password_hash": row[2],
        "role": row[3], "full_name": row[4], "email": row[5],
        "is_active": bool(row[6]), "failed_logins": row[7],
        "locked_until": row[8], "last_login": row[9],
        "matricula": row[10], "especialidad": row[11],
        "telefono": row[12], "hospital": row[13], "doctor_id": row[14]
    }


def get_user_by_id(user_id: int) -> dict | None:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT u.id, u.username, u.password_hash, u.role, u.full_name,
                  u.email, u.is_active, u.failed_logins, u.locked_until, u.last_login,
                  d.matricula, d.especialidad, d.telefono, d.hospital, d.id AS doctor_id
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
    return {
        "id": row[0], "username": row[1], "password_hash": row[2],
        "role": row[3], "full_name": row[4], "email": row[5],
        "is_active": bool(row[6]), "failed_logins": row[7],
        "locked_until": _fmt_date(row[8]), "last_login": _fmt_date(row[9]),
        "matricula": row[10], "especialidad": row[11],
        "telefono": row[12], "hospital": row[13], "doctor_id": row[14]
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
        "matricula": user.get("matricula"), "doctor_id": user.get("doctor_id")
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
                telefono: str = None, hospital: str = None) -> dict | None:
    if get_user_by_username(username):
        return None
    pw_hash = generate_password_hash(password)
    conn    = get_connection()
    cursor  = conn.cursor()
    cursor.execute(
        "EXEC dbo.sp_create_user ?, ?, ?, ?, ?, ?, ?, ?, ?",
        username, pw_hash, role, full_name, email,
        matricula, especialidad, telefono, hospital
    )
    cursor.fetchone()
    cursor.close()
    conn.close()
    return get_user_by_username(username)


def update_user(user_id: int, username: str = None, password: str = None,
                role: str = None, full_name: str = None, email: str = None,
                is_active: bool = None, matricula: str = None,
                especialidad: str = None, telefono: str = None,
                hospital: str = None) -> dict | None:
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
            "EXEC dbo.sp_update_user ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
            user_id, username, pw_hash, role, full_name, email,
            is_active_val, matricula, especialidad, telefono, hospital
        )
        cursor.fetchone()
    except pyodbc.Error:
        pass
    finally:
        cursor.close()
        conn.close()
    return get_user_by_id(user_id)


def list_users() -> list:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, username, role, full_name, email, is_active,
                  failed_logins, locked_until, last_login, created_at,
                  matricula, especialidad, telefono, hospital, doctor_id
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
        "SELECT id, cedula, name, dob, gender, phone, blood_type, age, antecedentes, created_at, updated_at, photo_url "
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
        "updated_at": _fmt_date(row[10]), "photo_url": row[11]
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
                 constantes: dict = None, sintomas: dict = None) -> int | None:
    """Crea una nueva visita médica y guarda constantes y síntomas."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "EXEC dbo.sp_create_visit ?, ?, ?, ?, ?, ?",
        patient_id, doctor_id, visit_type, motivo_consulta, motivo_emergencia, doctor_notes
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
                  alert_level, alert_color, specialist
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
        "parent_appointment_id": row[22]
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
    visits_by_week = [
        {"year": r[0], "week": r[1], "total": r[2]}
        for r in cursor.fetchall()
    ]

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
    diag_dist = [
        {"diagnosis": r[0], "count": r[1]}
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
    patients_growth = [
        {"year": r[0], "month": r[1], "total": r[2]}
        for r in cursor.fetchall()
    ]

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
        "visits_by_week":  visits_by_week,
        "diag_distribution": diag_dist,
        "patients_growth": patients_growth,
        "visit_types":     visit_types,
    }


# ─── SETTINGS AVANZADOS ───────────────────────────────────────────────────────

SETTINGS_KEYS = [
    "clinic_name", "clinic_address", "clinic_phone",
    "clinic_rnc",  "clinic_hours",   "clinic_email",
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
