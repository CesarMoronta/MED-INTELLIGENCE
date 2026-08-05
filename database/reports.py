import json
from datetime import datetime, date
from database.connection import get_connection, get_db_cursor, rows_to_dicts, _fmt_date, MAX_LOGIN_ATTEMPTS, LOCKOUT_MINUTES

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
            SUM(CASE WHEN status='abierta' THEN 1 ELSE 0 END),
            SUM(CASE WHEN CAST(scheduled_date AS DATE) = CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END),
            SUM(CASE WHEN CAST(scheduled_date AS DATE) = CAST(DATEADD(day,1,GETDATE()) AS DATE) THEN 1 ELSE 0 END),
            SUM(CASE WHEN status='completada' AND YEAR(scheduled_date) = YEAR(GETDATE()) AND MONTH(scheduled_date) = MONTH(GETDATE()) THEN 1 ELSE 0 END)
        FROM dbo.appointments
        WHERE doctor_id = ? AND status != 'cancelada'
    """, doctor_id)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return {
        "citas_pendientes": row[0] or 0,
        "citas_hoy": row[1] or 0,
        "citas_manana": row[2] or 0,
        "citas_mes": row[3] or 0,
    } if row else {"citas_pendientes": 0, "citas_hoy": 0, "citas_manana": 0, "citas_mes": 0}

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

def get_epidemiology_report(date_from: str = None, date_to: str = None, doctor_id: int = None) -> dict:
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Construir las condiciones WHERE comunes para filtrar por visitas
    where_clauses = ["1=1"]
    params = []

    if date_from:
        where_clauses.append("v.visit_date >= ?")
        params.append(date_from + " 00:00:00")
    if date_to:
        where_clauses.append("v.visit_date <= ?")
        params.append(date_to + " 23:59:59")
    if doctor_id:
        where_clauses.append("v.doctor_id = ?")
        params.append(doctor_id)

    where_sql = " AND ".join(where_clauses)

    # A. Diagnósticos por País de Residencia
    # Solo mostrar los países con pacientes registrados y no nulos
    query_country = f"""
        SELECT p.residence_country, d.diagnosis_primary, COUNT(DISTINCT p.id) AS patient_count
        FROM dbo.patients p
        JOIN dbo.emergency_visits v ON p.id = v.patient_id
        JOIN dbo.diagnoses d ON v.id = d.visit_id
        WHERE p.residence_country IS NOT NULL AND p.residence_country <> '' AND d.phase = 'final' AND {where_sql}
        GROUP BY p.residence_country, d.diagnosis_primary
        ORDER BY p.residence_country ASC, patient_count DESC
    """
    cursor.execute(query_country, params)
    by_country = rows_to_dicts(cursor)

    # B. Diagnósticos por Etnia
    query_ethnicity = f"""
        SELECT p.ethnicity, d.diagnosis_primary, COUNT(DISTINCT p.id) AS patient_count
        FROM dbo.patients p
        JOIN dbo.emergency_visits v ON p.id = v.patient_id
        JOIN dbo.diagnoses d ON v.id = d.visit_id
        WHERE p.ethnicity IS NOT NULL AND p.ethnicity <> '' AND d.phase = 'final' AND {where_sql}
        GROUP BY p.ethnicity, d.diagnosis_primary
        ORDER BY p.ethnicity ASC, patient_count DESC
    """
    cursor.execute(query_ethnicity, params)
    by_ethnicity = rows_to_dicts(cursor)

    # C. Diagnósticos por Rango de Edad
    query_age = f"""
        SELECT 
            CASE 
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 12 THEN 'Pediátrico (0-12)'
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 18 THEN 'Adolescente (13-18)'
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 35 THEN 'Adulto Joven (19-35)'
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 50 THEN 'Adulto (36-50)'
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 65 THEN 'Adulto Mayor (51-65)'
                ELSE 'Geriátrico (66+)'
            END AS age_range,
            d.diagnosis_primary,
            COUNT(DISTINCT p.id) AS patient_count
        FROM dbo.patients p
        JOIN dbo.emergency_visits v ON p.id = v.patient_id
        JOIN dbo.diagnoses d ON v.id = d.visit_id
        WHERE d.phase = 'final' AND {where_sql}
        GROUP BY 
            CASE 
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 12 THEN 'Pediátrico (0-12)'
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 18 THEN 'Adolescente (13-18)'
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 35 THEN 'Adulto Joven (19-35)'
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 50 THEN 'Adulto (36-50)'
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 65 THEN 'Adulto Mayor (51-65)'
                ELSE 'Geriátrico (66+)'
            END,
            d.diagnosis_primary
        ORDER BY age_range ASC, patient_count DESC
    """
    cursor.execute(query_age, params)
    by_age = rows_to_dicts(cursor)

    # D. Prescripciones por Perfil de Paciente (Etnia, País, Grupo de Edad)
    # 1. Por Etnia
    query_meds_ethnicity = f"""
        SELECT p.ethnicity AS profile_value, rx.medication, COUNT(rx.id) AS prescription_count
        FROM dbo.patients p
        JOIN dbo.emergency_visits v ON p.id = v.patient_id
        JOIN dbo.prescriptions rx ON v.id = rx.visit_id
        WHERE p.ethnicity IS NOT NULL AND p.ethnicity <> '' AND {where_sql}
        GROUP BY p.ethnicity, rx.medication
        ORDER BY p.ethnicity ASC, prescription_count DESC
    """
    cursor.execute(query_meds_ethnicity, params)
    meds_by_ethnicity = rows_to_dicts(cursor)
    for m in meds_by_ethnicity:
        m["profile_type"] = "Etnia"

    # 2. Por País
    query_meds_country = f"""
        SELECT p.residence_country AS profile_value, rx.medication, COUNT(rx.id) AS prescription_count
        FROM dbo.patients p
        JOIN dbo.emergency_visits v ON p.id = v.patient_id
        JOIN dbo.prescriptions rx ON v.id = rx.visit_id
        WHERE p.residence_country IS NOT NULL AND p.residence_country <> '' AND {where_sql}
        GROUP BY p.residence_country, rx.medication
        ORDER BY p.residence_country ASC, prescription_count DESC
    """
    cursor.execute(query_meds_country, params)
    meds_by_country = rows_to_dicts(cursor)
    for m in meds_by_country:
        m["profile_type"] = "País Residencia"

    # 3. Por Edad
    query_meds_age = f"""
        SELECT 
            CASE 
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 12 THEN 'Pediátrico (0-12)'
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 18 THEN 'Adolescente (13-18)'
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 35 THEN 'Adulto Joven (19-35)'
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 50 THEN 'Adulto (36-50)'
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 65 THEN 'Adulto Mayor (51-65)'
                ELSE 'Geriátrico (66+)'
            END AS profile_value,
            rx.medication,
            COUNT(rx.id) AS prescription_count
        FROM dbo.patients p
        JOIN dbo.emergency_visits v ON p.id = v.patient_id
        JOIN dbo.prescriptions rx ON v.id = rx.visit_id
        WHERE {where_sql}
        GROUP BY 
            CASE 
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 12 THEN 'Pediátrico (0-12)'
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 18 THEN 'Adolescente (13-18)'
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 35 THEN 'Adulto Joven (19-35)'
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 50 THEN 'Adulto (36-50)'
                WHEN (DATEDIFF(YEAR, p.dob, GETDATE()) - CASE WHEN MONTH(p.dob) > MONTH(GETDATE()) OR (MONTH(p.dob) = MONTH(GETDATE()) AND DAY(p.dob) > DAY(GETDATE())) THEN 1 ELSE 0 END) <= 65 THEN 'Adulto Mayor (51-65)'
                ELSE 'Geriátrico (66+)'
            END,
            rx.medication
        ORDER BY profile_value ASC, prescription_count DESC
    """
    cursor.execute(query_meds_age, params)
    meds_by_age = rows_to_dicts(cursor)
    for m in meds_by_age:
        m["profile_type"] = "Rango Edad"

    # Consolidar medicamentos prescritos por perfiles
    meds_by_profile = meds_by_ethnicity + meds_by_country + meds_by_age

    cursor.close()
    conn.close()

    return {
        "success": True,
        "by_country": by_country,
        "by_ethnicity": by_ethnicity,
        "by_age": by_age,
        "meds_by_profile": meds_by_profile
    }
