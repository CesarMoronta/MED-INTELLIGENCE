import io
import csv
from flask import Blueprint, request, jsonify, send_file, make_response
from database import (get_visit_with_details, get_prescriptions, get_visit_tests,
                      list_appointments, get_all_clinic_settings,
                      list_patients, list_clinical_history, get_invoice_by_id,
                      log_audit_action)
from utils import requires_login, requires_role, get_current_user, get_client_ip
from utils.pdf_generator import (generate_prescription_pdf,
                                  generate_lab_order_pdf,
                                  generate_daily_schedule_pdf,
                                  generate_invoice_pdf)

pdf_bp = Blueprint("pdf_bp", __name__)



# ─── PDF: Receta Médica ───────────────────────────────────────────────────────

@pdf_bp.route("/api/pdf/prescription/<int:visit_id>", methods=["GET"])
@requires_login
@requires_role("doctor", "admin")
def api_pdf_prescription(visit_id):
    visit         = get_visit_with_details(visit_id)
    if not visit:
        return jsonify({"success": False, "error": "Visita no encontrada."}), 404
    prescriptions = get_prescriptions(visit_id)
    clinic_info   = get_all_clinic_settings()

    pdf_bytes = generate_prescription_pdf(visit, prescriptions, clinic_info)
    
    u = get_current_user()
    log_audit_action(
        username=u.get("username"), action="EXPORT", entity="Prescription",
        entity_id=str(visit_id),
        details=f"Descargó PDF de receta médica de la visita ID {visit_id} para el paciente '{visit.get('patient_name')}' (ID: {visit.get('patient_id')})",
        ip_address=get_client_ip(), user_id=u.get("id")
    )

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"receta_visita_{visit_id}.pdf"
    )


# ─── PDF: Orden de Laboratorio ────────────────────────────────────────────────

@pdf_bp.route("/api/pdf/lab_order/<int:visit_id>", methods=["GET"])
@requires_login
@requires_role("doctor", "admin")
def api_pdf_lab_order(visit_id):
    visit       = get_visit_with_details(visit_id)
    if not visit:
        return jsonify({"success": False, "error": "Visita no encontrada."}), 404
    tests       = get_visit_tests(visit_id)
    clinic_info = get_all_clinic_settings()

    pdf_bytes = generate_lab_order_pdf(visit, tests, clinic_info)

    u = get_current_user()
    log_audit_action(
        username=u.get("username"), action="EXPORT", entity="LabOrder",
        entity_id=str(visit_id),
        details=f"Descargó PDF de orden de laboratorio de la visita ID {visit_id} para el paciente '{visit.get('patient_name')}' (ID: {visit.get('patient_id')})",
        ip_address=get_client_ip(), user_id=u.get("id")
    )

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"orden_lab_visita_{visit_id}.pdf"
    )


# ─── PDF: Agenda del Día ──────────────────────────────────────────────────────

@pdf_bp.route("/api/pdf/schedule", methods=["GET"])
@pdf_bp.route("/api/pdf/agenda", methods=["GET"])   # alias JS
@requires_login
def api_pdf_schedule():
    from datetime import date
    day_str     = request.args.get("date", str(date.today()))
    doctor_id   = request.args.get("doctor_id", type=int)
    u           = get_current_user()
    if u["role"] == "doctor":
        doctor_id = u["id"]

    appointments = list_appointments(doctor_id=doctor_id, date_filter=day_str)
    clinic_info  = get_all_clinic_settings()

    pdf_bytes = generate_daily_schedule_pdf(appointments, day_str, clinic_info)
    
    log_audit_action(
        username=u.get("username"), action="EXPORT", entity="Schedule",
        details=f"Descargó PDF de la agenda para el día {day_str} (Doctor ID: {doctor_id or 'Todos'})",
        ip_address=get_client_ip(), user_id=u.get("id")
    )

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"agenda_{day_str}.pdf"
    )


# ─── CSV: Exportar Pacientes ──────────────────────────────────────────────────

@pdf_bp.route("/api/export/patients.csv", methods=["GET"])
@requires_login
@requires_role("admin")
def api_export_patients_csv():
    patients = list_patients()
    output   = io.StringIO()
    writer   = csv.writer(output)
    writer.writerow(["ID", "Cedula", "Nombre", "Fecha Nacimiento", "Genero",
                     "Telefono", "Tipo Sangre", "Fecha Registro"])
    for p in patients:
        writer.writerow([
            p.get("id"), p.get("cedula"), p.get("name"),
            p.get("dob"), p.get("gender"), p.get("phone"),
            p.get("blood_type"), p.get("created_at")
        ])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=pacientes.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"

    u = get_current_user()
    log_audit_action(
        username=u.get("username"), action="EXPORT", entity="Patient",
        details="Exportó listado completo de pacientes a CSV",
        ip_address=get_client_ip(), user_id=u.get("id")
    )

    return response


# ─── CSV: Exportar Historial Clínico ─────────────────────────────────────────

@pdf_bp.route("/api/export/history.csv", methods=["GET"])
@requires_login
@requires_role("admin")
def api_export_history_csv():
    history = list_clinical_history()
    output  = io.StringIO()
    writer  = csv.writer(output)
    writer.writerow(["ID Visita", "Fecha Visita", "Tipo", "Paciente", "Cedula",
                     "Doctor", "Diagnostico Principal", "Probabilidad", "Nivel Alerta",
                     "Especialista"])
    for h in history:
        writer.writerow([
            h.get("visit_id"), h.get("visit_date"), h.get("visit_type"),
            h.get("patient_name"), h.get("patient_cedula"),
            h.get("doctor_fullname"), h.get("diagnosis_primary"),
            h.get("probability"), h.get("alert_level"), h.get("specialist")
        ])

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=historial_clinico.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"

    u = get_current_user()
    log_audit_action(
        username=u.get("username"), action="EXPORT", entity="History",
        details="Exportó historial clínico completo a CSV",
        ip_address=get_client_ip(), user_id=u.get("id")
    )

    return response


# ─── SQL: Backup Completo del Sistema ─────────────────────────────────────────

def generate_database_sql_dump() -> str:
    """
    Genera un script SQL (.sql) completo con la estructura (Tablas, Vistas,
    Procedimientos Almacenados, Triggers, Índices) y todos los datos del sistema.
    """
    import os
    from datetime import datetime
    from database import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "-- =============================================================================",
        "-- MED-INTELLIGENCE PRO - Respaldo Completo de Base de Datos",
        f"-- Generado: {timestamp_str}",
        "-- Incluye: Esquema (Tablas, Vistas, Procedimientos, Triggers, Índices) y Datos",
        "-- =============================================================================",
        "SET NOCOUNT ON;",
        "GO",
        ""
    ]

    # 1. Incluir el Esquema de Base de Datos DDL (Tablas, Vistas, Stored Procedures, Triggers, Índices)
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database_schema.txt")
    if not os.path.exists(schema_path):
        schema_path = "database_schema.txt"

    lines.append("-- =============================================================================")
    lines.append("-- SECCIÓN A: ESTRUCTURA Y ESQUEMA (Tablas, Vistas, Triggers, Procedimientos)")
    lines.append("-- =============================================================================")
    lines.append("")

    if os.path.exists(schema_path):
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_content = f.read()
                lines.append(schema_content)
                lines.append("")
        except Exception as ex_file:
            lines.append(f"-- (No se pudo leer el archivo de esquema local: {str(ex_file)})")
            lines.append("")

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
    except Exception as ex_conn:
        lines.append(f"-- ADVERTENCIA: No se pudo conectar a la base de datos para extraer datos en vivo: {str(ex_conn)}")
        lines.append("-- Fin del Respaldo (Solo Esquema)")
        lines.append("GO")
        return "\n".join(lines)

    # Intentar extraer dinámicamente Vistas, Triggers y Procedimientos Almacenados directamente del catálogo de SQL Server si existen
    try:
        # Vistas
        cursor.execute("""
            SELECT v.name, m.definition
            FROM sys.views v
            JOIN sys.sql_modules m ON v.object_id = m.object_id
            WHERE v.is_ms_shipped = 0
            ORDER BY v.name
        """)
        views = cursor.fetchall()
        if views:
            lines.append("-- ─── Vistas Activas de la Base de Datos ──────────────────────────────────")
            for view_name, definition in views:
                if definition:
                    lines.append(f"IF OBJECT_ID(N'dbo.[{view_name}]', N'V') IS NOT NULL DROP VIEW dbo.[{view_name}];")
                    lines.append("GO")
                    lines.append(definition.strip())
                    lines.append("\nGO\n")

        # Procedimientos y Funciones
        cursor.execute("""
            SELECT p.name, m.definition, p.type_desc
            FROM sys.objects p
            JOIN sys.sql_modules m ON p.object_id = m.object_id
            WHERE p.type IN ('P', 'FN', 'IF', 'TF') AND p.is_ms_shipped = 0
            ORDER BY p.type, p.name
        """)
        procs = cursor.fetchall()
        if procs:
            lines.append("-- ─── Procedimientos y Funciones Activos ──────────────────────────────────")
            for proc_name, definition, p_type in procs:
                if definition:
                    lines.append(definition.strip())
                    lines.append("\nGO\n")

        # Triggers
        cursor.execute("""
            SELECT t.name, m.definition
            FROM sys.triggers t
            JOIN sys.sql_modules m ON t.object_id = m.object_id
            WHERE t.is_ms_shipped = 0
            ORDER BY t.name
        """)
        triggers = cursor.fetchall()
        if triggers:
            lines.append("-- ─── Triggers Activos de la Base de Datos ───────────────────────────────")
            for trig_name, definition in triggers:
                if definition:
                    lines.append(definition.strip())
                    lines.append("\nGO\n")
    except Exception:
        # Silencioso si se usa un mock o controlador sin catalogos sys completos
        pass

    # 2. Exportación de Datos (INSERT INTO) de todas las tablas base con desactivación de restricciones
    lines.append("-- =============================================================================")
    lines.append("-- SECCIÓN B: REGISTROS Y DATOS COMPLETOS (DML - INSERT INTO)")
    lines.append("-- =============================================================================")
    lines.append("")
    lines.append("-- Desactivar temporalmente Foreign Keys y Triggers para permitir inserción en cualquier orden")
    lines.append("EXEC sp_MSforeachtable \"ALTER TABLE ? NOCHECK CONSTRAINT ALL\";")
    lines.append("EXEC sp_MSforeachtable \"ALTER TABLE ? DISABLE TRIGGER ALL\";")
    lines.append("GO")
    lines.append("")

    try:
        cursor.execute("""
            SELECT TABLE_SCHEMA, TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA NOT IN ('sys')
            ORDER BY TABLE_NAME
        """)
        tables = cursor.fetchall()

        for row in (tables or []):
            if not isinstance(row, (tuple, list)) or len(row) < 2:
                continue
            schema_name, table_name = row[0], row[1]
            full_table = f"[{schema_name}].[{table_name}]"
            lines.append(f"-- -----------------------------------------------------------------------------")
            lines.append(f"-- Tabla: {full_table}")
            lines.append(f"-- -----------------------------------------------------------------------------")

            cursor.execute(f"SELECT * FROM {full_table}")
            if cursor.description is None:
                lines.append("-- (Sin descripción)")
                lines.append("")
                continue

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            if not rows:
                lines.append("-- (Sin registros)")
                lines.append("")
                continue

            cols_str = ", ".join([f"[{col}]" for col in columns])

            lines.append(f"DELETE FROM {full_table};")
            lines.append(f"IF OBJECTPROPERTY(OBJECT_ID(N'{full_table}'), 'TableHasIdentity') = 1 SET IDENTITY_INSERT {full_table} ON;")

            for r in rows:
                vals = []
                for val in r:
                    if val is None:
                        vals.append("NULL")
                    elif isinstance(val, bool):
                        vals.append("1" if val else "0")
                    elif isinstance(val, (int, float)):
                        vals.append(str(val))
                    elif hasattr(val, "isoformat"):
                        vals.append(f"'{val.isoformat()}'")
                    elif isinstance(val, (bytes, bytearray)):
                        vals.append(f"0x{val.hex()}")
                    else:
                        s_val = str(val).replace("'", "''")
                        vals.append(f"N'{s_val}'")

                vals_str = ", ".join(vals)
                lines.append(f"INSERT INTO {full_table} ({cols_str}) VALUES ({vals_str});")

            lines.append(f"IF OBJECTPROPERTY(OBJECT_ID(N'{full_table}'), 'TableHasIdentity') = 1 SET IDENTITY_INSERT {full_table} OFF;")
            lines.append("GO")
            lines.append("")

        lines.append("-- -----------------------------------------------------------------------------")
        lines.append("-- Reactivación de Restricciones y Triggers de la Base de Datos")
        lines.append("-- -----------------------------------------------------------------------------")
        lines.append("EXEC sp_MSforeachtable \"ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL\";")
        lines.append("EXEC sp_MSforeachtable \"ALTER TABLE ? ENABLE TRIGGER ALL\";")
        lines.append("GO")
        lines.append("")
        lines.append("-- Fin del Respaldo Completo")
        lines.append("GO")
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass

    return "\n".join(lines)


@pdf_bp.route("/api/export/backup.sql", methods=["GET"])
@requires_login
@requires_role("admin")
def api_export_backup_sql():
    from datetime import datetime
    sql_content = generate_database_sql_dump()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"med_intelligence_backup_{timestamp}.sql"

    response = make_response(sql_content)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "application/sql; charset=utf-8"

    u = get_current_user()
    log_audit_action(
        username=u.get("username"), action="EXPORT", entity="DatabaseBackup",
        details=f"Exportó respaldo completo de base de datos ({filename})",
        ip_address=get_client_ip(), user_id=u.get("id")
    )

    return response


# ─── PDF: Factura Electrónica (e-CF) ──────────────────────────────────────────

@pdf_bp.route("/api/pdf/invoice/<int:invoice_id>", methods=["GET"])
@requires_login
def api_pdf_invoice(invoice_id):
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        return jsonify({"success": False, "error": "Factura no encontrada."}), 404
    
    clinic_info = get_all_clinic_settings()
    pdf_bytes = generate_invoice_pdf(invoice, clinic_info)
    
    u = get_current_user()
    log_audit_action(
        username=u.get("username"), action="EXPORT", entity="Billing",
        entity_id=str(invoice_id),
        details=f"Descargó PDF de factura ID {invoice_id} (e-CF: {invoice.get('encf') or 'N/A'})",
        ip_address=get_client_ip(), user_id=u.get("id")
    )

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"factura_{invoice.get('encf') or invoice_id}.pdf"
    )

