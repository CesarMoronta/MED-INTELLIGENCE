import json
from datetime import datetime, date
from database.connection import get_connection, get_db_cursor, rows_to_dicts, _fmt_date, MAX_LOGIN_ATTEMPTS, LOCKOUT_MINUTES
from utils import format_cedula

def add_patient(cedula: str, name: str, dob: str, gender: str,
                antecedentes: dict, phone: str = None,
                blood_type: str = None, registered_by: int = None,
                photo_url: str = None, birth_country: str = None,
                birth_city: str = None, residence_country: str = None,
                residence_city: str = None, ethnicity: str = None,
                past_surgeries: str = None, education_level: str = None,
                occupation: str = None, marital_status: str = None) -> int | None:
    """Crea un nuevo paciente. Retorna el ID del paciente si tuvo éxito, None si ya existe o falla."""
    name = (name or "").strip().upper()
    conn      = get_connection()
    cursor    = conn.cursor()
    patient_id = None
    try:
        cursor.execute(
            "EXEC dbo.sp_create_patient ?, ?, ?, ?, ?, ?, ?, ?, 'Vivo', NULL, NULL, NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?",
            cedula, name, dob, gender, phone, blood_type, registered_by, photo_url,
            birth_country, birth_city, residence_country, residence_city, ethnicity,
            past_surgeries, education_level, occupation, marital_status
        )
        row        = cursor.fetchone()
        patient_id = int(row[0]) if row else None
    except pyodbc.IntegrityError:
        return None
    except Exception as e:
        print(f"Error en add_patient: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

    if not patient_id:
        return None
    _set_patient_antecedents(patient_id, antecedentes)
    return patient_id

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
        "SELECT id, cedula, name, dob, gender, phone, blood_type, age, antecedentes, created_at, updated_at, photo_url, vital_status, death_date, death_certificate_url, death_notes, "
        "birth_country, birth_city, residence_country, residence_city, ethnicity, past_surgeries, education_level, occupation, marital_status "
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
        "death_certificate_url": row[14], "death_notes": row[15],
        "birth_country": row[16], "birth_city": row[17],
        "residence_country": row[18], "residence_city": row[19],
        "ethnicity": row[20], "past_surgeries": row[21],
        "education_level": row[22], "occupation": row[23],
        "marital_status": row[24]
    }
    if row[8]:
        parsed = json.loads(row[8])
        patient["antecedentes"] = {item["antecedent"]: bool(item["value"]) for item in parsed}
    return patient

def list_patients(search: str = None, doctor_id: int = None) -> list:
    conn   = get_connection()
    cursor = conn.cursor()
    
    base_query = (
        "SELECT p.id, p.cedula, p.name, p.dob, p.gender, p.phone, p.blood_type, p.age, p.antecedentes, p.photo_url, "
        "p.birth_country, p.birth_city, p.residence_country, p.residence_city, p.ethnicity, p.past_surgeries, "
        "p.education_level, p.occupation, p.marital_status "
        "FROM dbo.vw_patients p"
    )
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
                   photo_url: str = None, birth_country: str = None,
                   birth_city: str = None, residence_country: str = None,
                   residence_city: str = None, ethnicity: str = None,
                   past_surgeries: str = None, education_level: str = None,
                   occupation: str = None, marital_status: str = None) -> bool:
    existing = get_patient(patient_id)
    if not existing:
        return False
    if name:
        name = name.strip().upper()
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "EXEC dbo.sp_update_patient ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
        patient_id,
        cedula   or None,
        name     or None,
        dob      or None,
        gender   or None,
        phone    or None,
        blood_type or None,
        photo_url or None,
        birth_country,
        birth_city,
        residence_country,
        residence_city,
        ethnicity,
        past_surgeries,
        education_level,
        occupation,
        marital_status
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
