import json
from datetime import datetime, date
from database.connection import get_connection, get_db_cursor, rows_to_dicts, _fmt_date, MAX_LOGIN_ATTEMPTS, LOCKOUT_MINUTES
import calendar

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
    query += " ORDER BY a.scheduled_date DESC, a.scheduled_time DESC"

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
        "SET NOCOUNT ON; INSERT INTO dbo.appointments (patient_id, doctor_id, scheduled_date, scheduled_time, notes, parent_appointment_id) VALUES (?, ?, ?, ?, ?, ?); SELECT SCOPE_IDENTITY();",
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

def get_appointment(appointment_id: int) -> dict:
    """Obtiene los detalles de una cita por su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, patient_id, doctor_id, scheduled_date, scheduled_time, status, notes, confirmed, parent_appointment_id FROM dbo.appointments WHERE id = ?",
        appointment_id
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return {
            "id": row[0],
            "patient_id": row[1],
            "doctor_id": row[2],
            "scheduled_date": _fmt_date(row[3]),
            "scheduled_time": str(row[4]) if row[4] else None,
            "status": row[5],
            "notes": row[6],
            "confirmed": bool(row[7]),
            "parent_appointment_id": row[8]
        }
    return None

def check_appointment_clash(appointment_id: int) -> bool:
    """
    Verifica si los datos de la cita (doctor, fecha, hora) chocan con otra cita activa.
    Se usa al reactivar una cita cancelada.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT doctor_id, scheduled_date, scheduled_time FROM dbo.appointments WHERE id = ?", appointment_id)
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return False
    doctor_id, scheduled_date, scheduled_time = row
    
    # Buscamos si hay otra cita activa para el mismo doctor, fecha y hora
    cursor.execute(
        "SELECT COUNT(*) FROM dbo.appointments WHERE doctor_id = ? AND scheduled_date = ? AND scheduled_time = ? AND status IN ('abierta', 'en_curso', 'completada') AND id <> ?",
        doctor_id, scheduled_date, scheduled_time, appointment_id
    )
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count > 0

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
