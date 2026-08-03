import json
from datetime import datetime, date
from database.connection import get_connection, get_db_cursor, rows_to_dicts, _fmt_date, MAX_LOGIN_ATTEMPTS, LOCKOUT_MINUTES

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
