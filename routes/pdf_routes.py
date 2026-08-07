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
        details=f"Descargó PDF de receta médica de la visita ID {visit_id} para paciente ID {visit.get('patient_id')}",
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
        details=f"Descargó PDF de orden de laboratorio de la visita ID {visit_id} para paciente ID {visit.get('patient_id')}",
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

