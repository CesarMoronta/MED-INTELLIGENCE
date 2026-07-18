"""pdf_generator.py — Generación de PDFs profesionales con ReportLab.

Funciones:
  generate_prescription_pdf  — Receta médica
  generate_lab_order_pdf     — Orden de laboratorio / imagenología
  generate_daily_schedule_pdf — Agenda del día
"""
from __future__ import annotations

import io
from datetime import datetime, date
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing


# ─── Paleta de colores ─────────────────────────────────────────────────────────
PRIMARY    = colors.HexColor("#1a6fc4")
ACCENT     = colors.HexColor("#0ea5e9")
DARK_BG    = colors.HexColor("#1e293b")
LIGHT_GREY = colors.HexColor("#f1f5f9")
MID_GREY   = colors.HexColor("#94a3b8")
SUCCESS    = colors.HexColor("#10b981")
DANGER     = colors.HexColor("#ef4444")
WHITE      = colors.white
BLACK      = colors.black


def _base_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ClinicHeader",
        fontSize=20,
        fontName="Helvetica-Bold",
        textColor=WHITE,
        alignment=TA_LEFT,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="ClinicSubHeader",
        fontSize=9,
        fontName="Helvetica",
        textColor=colors.HexColor("#cbd5e1"),
        alignment=TA_LEFT,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontSize=11,
        fontName="Helvetica-Bold",
        textColor=PRIMARY,
        spaceBefore=12,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="BodyText2",
        fontSize=9,
        fontName="Helvetica",
        textColor=BLACK,
        leading=14,
    ))
    styles.add(ParagraphStyle(
        name="SmallMuted",
        fontSize=8,
        fontName="Helvetica",
        textColor=MID_GREY,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="Footer",
        fontSize=7,
        fontName="Helvetica",
        textColor=MID_GREY,
        alignment=TA_CENTER,
    ))
    return styles


def _build_header(story: list, clinic_info: dict, title: str, subtitle: str, styles) -> None:
    """Construye el bloque header con fondo azul oscuro."""
    clinic_name = clinic_info.get("clinic_name", "Consultorio Médico")
    clinic_addr = clinic_info.get("clinic_address", "")
    clinic_tel  = clinic_info.get("clinic_phone", "")
    clinic_rnc  = clinic_info.get("clinic_rnc", "")

    info_lines = []
    if clinic_addr:
        info_lines.append(clinic_addr)
    if clinic_tel:
        info_lines.append(f"Tel: {clinic_tel}")
    if clinic_rnc:
        info_lines.append(f"RNC: {clinic_rnc}")

    left_col = [
        Paragraph(clinic_name, styles["ClinicHeader"]),
        Paragraph("<br/>".join(info_lines) if info_lines else "", styles["ClinicSubHeader"]),
    ]
    right_col = [
        Paragraph(
            f'<font color="#93c5fd" size="14"><b>{title}</b></font>',
            ParagraphStyle("RTitle", fontSize=14, fontName="Helvetica-Bold",
                           textColor=colors.HexColor("#93c5fd"), alignment=TA_RIGHT)
        ),
        Paragraph(
            subtitle,
            ParagraphStyle("RSub", fontSize=9, fontName="Helvetica",
                           textColor=colors.HexColor("#cbd5e1"), alignment=TA_RIGHT)
        ),
    ]

    header_table = Table(
        [[left_col, right_col]],
        colWidths=["60%", "40%"],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), DARK_BG),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (0, 0),  16),
        ("RIGHTPADDING",  (1, 0), (1, 0),  16),
        ("TOPPADDING",    (0, 0), (-1, -1), 16),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
        ("ROUNDEDCORNERS", (0, 0), (-1, -1), [8, 8, 8, 8]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 16))


def _patient_info_table(visit: dict, styles) -> Table:
    """Bloque de datos del paciente con fondo gris claro."""
    fields = [
        ["Paciente",  visit.get("patient_name", "—")],
        ["Cédula",    visit.get("patient_cedula", "—")],
        ["Doctor",    visit.get("doctor_fullname") or visit.get("doctor_username", "—")],
        ["Fecha",     _fmt_date(visit.get("visit_date"))],
        ["Tipo",      (visit.get("visit_type") or "consulta").title()],
    ]
    rows = [
        [
            Paragraph(f"<b>{k}:</b>", ParagraphStyle("PK", fontSize=9, fontName="Helvetica-Bold",
                                                       textColor=PRIMARY)),
            Paragraph(str(v), ParagraphStyle("PV", fontSize=9, fontName="Helvetica")),
        ]
        for k, v in fields
    ]
    tbl = Table(rows, colWidths=["30%", "70%"])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_GREY),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_GREY, WHITE]),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    return tbl


def _fmt_date(dt) -> str:
    if not dt:
        return datetime.now().strftime("%d/%m/%Y")
    if isinstance(dt, (date, datetime)):
        return dt.strftime("%d/%m/%Y")
    try:
        return str(dt)[:10]
    except Exception:
        return "—"


def _footer_text(clinic_info: dict) -> str:
    name = clinic_info.get("clinic_name", "Consultorio Médico")
    return (
        f"Documento generado por {name} · {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
        "Este documento tiene validez médica oficial."
    )


# ─── Receta Médica ─────────────────────────────────────────────────────────────

def generate_prescription_pdf(visit: dict, prescriptions: list,
                               clinic_info: dict) -> bytes:
    """Genera el PDF de receta médica y retorna los bytes."""
    buf    = io.BytesIO()
    doc    = SimpleDocTemplate(buf, pagesize=letter,
                                rightMargin=0.75*inch, leftMargin=0.75*inch,
                                topMargin=0.5*inch, bottomMargin=0.75*inch)
    styles = _base_styles()
    story  = []

    _build_header(story, clinic_info, "RECETA MÉDICA",
                  f"Fecha: {_fmt_date(visit.get('visit_date'))}", styles)

    # Datos del paciente
    story.append(Paragraph("Datos del Paciente", styles["SectionTitle"]))
    story.append(_patient_info_table(visit, styles))
    story.append(Spacer(1, 16))

    # Motivo de consulta
    motivo = visit.get("motivo_consulta") or visit.get("motivo_emergencia", "")
    if motivo:
        story.append(Paragraph("Motivo de Consulta", styles["SectionTitle"]))
        story.append(Paragraph(motivo, styles["BodyText2"]))
        story.append(Spacer(1, 12))

    # Medicamentos
    story.append(Paragraph("Prescripción Médica", styles["SectionTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY))
    story.append(Spacer(1, 8))

    if prescriptions:
        header = [
            Paragraph("<b>#</b>", styles["BodyText2"]),
            Paragraph("<b>Medicamento</b>", styles["BodyText2"]),
            Paragraph("<b>Dosis</b>", styles["BodyText2"]),
            Paragraph("<b>Frecuencia</b>", styles["BodyText2"]),
            Paragraph("<b>Duración</b>", styles["BodyText2"]),
            Paragraph("<b>Cantidad</b>", styles["BodyText2"]),
        ]
        rows = [header]
        for i, rx in enumerate(prescriptions, 1):
            rows.append([
                Paragraph(str(i), styles["BodyText2"]),
                Paragraph(rx.get("medication", "—"), styles["BodyText2"]),
                Paragraph(rx.get("dosage", "—"), styles["BodyText2"]),
                Paragraph(rx.get("frequency", "—"), styles["BodyText2"]),
                Paragraph(f"{rx.get('duration_days', '—')} días", styles["BodyText2"]),
                Paragraph(str(rx.get("quantity", "—")), styles["BodyText2"]),
            ])
            if rx.get("notes"):
                rows.append([
                    Paragraph("", styles["BodyText2"]),
                    Paragraph(f"<i>Nota: {rx['notes']}</i>",
                               ParagraphStyle("Note", fontSize=8, fontName="Helvetica-Oblique",
                                              textColor=MID_GREY)),
                    "", "", "", "",
                ])

        tbl = Table(rows, colWidths=["5%", "30%", "15%", "20%", "15%", "15%"])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  PRIMARY),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0),  9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
            ("GRID",           (0, 0), (-1, -1), 0.5, MID_GREY),
            ("TOPPADDING",     (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
            ("LEFTPADDING",    (0, 0), (-1, -1), 6),
        ]))
        story.append(tbl)
    else:
        story.append(Paragraph("No se registraron medicamentos en esta visita.",
                                styles["BodyText2"]))

    # Notas del doctor
    notes = visit.get("doctor_notes", "")
    if notes:
        story.append(Spacer(1, 16))
        story.append(Paragraph("Indicaciones Adicionales", styles["SectionTitle"]))
        story.append(Paragraph(notes, styles["BodyText2"]))

    # Firma
    story.append(Spacer(1, 40))
    firma_table = Table(
        [[
            Paragraph("____________________________", styles["BodyText2"]),
            Paragraph("____________________________", styles["BodyText2"]),
        ], [
            Paragraph(f"<b>{visit.get('doctor_fullname', 'Dr./Dra.')}</b>",
                       ParagraphStyle("FirmName", fontSize=9, fontName="Helvetica-Bold",
                                      alignment=TA_CENTER)),
            Paragraph("<b>Sello del Consultorio</b>",
                       ParagraphStyle("Sello", fontSize=9, fontName="Helvetica-Bold",
                                      alignment=TA_CENTER)),
        ]],
        colWidths=["50%", "50%"],
    )
    firma_table.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                      ("TOPPADDING", (0, 0), (-1, -1), 4)]))
    story.append(firma_table)

    # Footer
    story.append(Spacer(1, 24))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GREY))
    story.append(Spacer(1, 6))
    story.append(Paragraph(_footer_text(clinic_info), styles["Footer"]))

    doc.build(story)
    return buf.getvalue()


# ─── Orden de Laboratorio ──────────────────────────────────────────────────────

def generate_lab_order_pdf(visit: dict, tests: list, clinic_info: dict) -> bytes:
    """Genera el PDF de orden de laboratorio/imagenología."""
    buf    = io.BytesIO()
    doc    = SimpleDocTemplate(buf, pagesize=letter,
                                rightMargin=0.75*inch, leftMargin=0.75*inch,
                                topMargin=0.5*inch, bottomMargin=0.75*inch)
    styles = _base_styles()
    story  = []

    _build_header(story, clinic_info, "ORDEN DE LABORATORIO",
                  f"Fecha: {_fmt_date(visit.get('visit_date'))}", styles)

    story.append(Paragraph("Datos del Paciente", styles["SectionTitle"]))
    story.append(_patient_info_table(visit, styles))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Exámenes Solicitados", styles["SectionTitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
    story.append(Spacer(1, 8))

    if tests:
        header = [
            Paragraph("<b>#</b>", styles["BodyText2"]),
            Paragraph("<b>Examen / Prueba</b>", styles["BodyText2"]),
            Paragraph("<b>Resultado</b>", styles["BodyText2"]),
            Paragraph("<b>Valor</b>", styles["BodyText2"]),
        ]
        rows = [header]
        for i, t in enumerate(tests, 1):
            resultado = t.get("result") or ("Pendiente" if not t.get("was_done") else "")
            rows.append([
                Paragraph(str(i), styles["BodyText2"]),
                Paragraph(t.get("test_name", "—"), styles["BodyText2"]),
                Paragraph(resultado, styles["BodyText2"]),
                Paragraph(t.get("result_value", ""), styles["BodyText2"]),
            ])

        tbl = Table(rows, colWidths=["5%", "45%", "25%", "25%"])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  ACCENT),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
            ("GRID",           (0, 0), (-1, -1), 0.5, MID_GREY),
            ("TOPPADDING",     (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
            ("LEFTPADDING",    (0, 0), (-1, -1), 6),
        ]))
        story.append(tbl)
    else:
        story.append(Paragraph("No se registraron exámenes en esta visita.", styles["BodyText2"]))

    # Instrucciones
    story.append(Spacer(1, 16))
    story.append(Paragraph("Instrucciones al Laboratorio", styles["SectionTitle"]))
    notes = visit.get("doctor_notes", "")
    story.append(Paragraph(
        notes or "Por favor procesar con urgencia según criterio clínico.",
        styles["BodyText2"]
    ))

    # Firma
    story.append(Spacer(1, 40))
    story.append(Paragraph("____________________________",
                             ParagraphStyle("Firma", fontSize=9, alignment=TA_CENTER)))
    story.append(Paragraph(
        f"<b>{visit.get('doctor_fullname', 'Dr./Dra.')}</b>",
        ParagraphStyle("FN", fontSize=9, fontName="Helvetica-Bold", alignment=TA_CENTER)
    ))

    story.append(Spacer(1, 24))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GREY))
    story.append(Spacer(1, 6))
    story.append(Paragraph(_footer_text(clinic_info), styles["Footer"]))

    doc.build(story)
    return buf.getvalue()


# ─── Agenda del Día ────────────────────────────────────────────────────────────

def generate_daily_schedule_pdf(appointments: list, day_str: str,
                                 clinic_info: dict) -> bytes:
    """Genera el PDF de agenda del día."""
    buf    = io.BytesIO()
    doc    = SimpleDocTemplate(buf, pagesize=letter,
                                rightMargin=0.75*inch, leftMargin=0.75*inch,
                                topMargin=0.5*inch, bottomMargin=0.75*inch)
    styles = _base_styles()
    story  = []

    try:
        d_obj    = datetime.strptime(day_str, "%Y-%m-%d")
        day_nice = d_obj.strftime("%A %d de %B de %Y")
    except Exception:
        day_nice = day_str

    _build_header(story, clinic_info, "AGENDA DEL DÍA", day_nice, styles)

    story.append(Paragraph(f"Total de citas: {len(appointments)}", styles["BodyText2"]))
    story.append(Spacer(1, 12))

    STATUS_COLORS = {
        "abierta":   colors.HexColor("#3b82f6"),
        "en_curso":  colors.HexColor("#f59e0b"),
        "completada": SUCCESS,
        "cancelada": DANGER,
    }

    if appointments:
        header = [
            Paragraph("<b>Hora</b>", styles["BodyText2"]),
            Paragraph("<b>Paciente</b>", styles["BodyText2"]),
            Paragraph("<b>Cédula</b>", styles["BodyText2"]),
            Paragraph("<b>Doctor</b>", styles["BodyText2"]),
            Paragraph("<b>Estado</b>", styles["BodyText2"]),
            Paragraph("<b>Notas</b>", styles["BodyText2"]),
        ]
        rows = [header]
        for a in appointments:
            status_color = STATUS_COLORS.get(a.get("status", "abierta"), MID_GREY)
            status_text  = (a.get("status") or "abierta").replace("_", " ").title()
            rows.append([
                Paragraph(str(a.get("scheduled_time", "—"))[:5], styles["BodyText2"]),
                Paragraph(a.get("patient_name", "—"), styles["BodyText2"]),
                Paragraph(a.get("patient_cedula", "—"), styles["BodyText2"]),
                Paragraph(a.get("doctor_fullname") or a.get("doctor_name", "—"),
                           styles["BodyText2"]),
                Paragraph(
                    f'<font color="white"><b>{status_text}</b></font>',
                    ParagraphStyle("StatusCell", fontSize=8, fontName="Helvetica-Bold",
                                   backColor=status_color, textColor=WHITE, alignment=TA_CENTER)
                ),
                Paragraph(a.get("notes", ""), styles["BodyText2"]),
            ])

        tbl = Table(rows, colWidths=["10%", "22%", "13%", "20%", "15%", "20%"])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  DARK_BG),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0),  9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
            ("GRID",           (0, 0), (-1, -1), 0.5, MID_GREY),
            ("TOPPADDING",     (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING",  (0, 0), (-1, -1), 7),
            ("LEFTPADDING",    (0, 0), (-1, -1), 6),
        ]))
        story.append(tbl)
    else:
        story.append(Paragraph("No hay citas programadas para este día.", styles["BodyText2"]))

    story.append(Spacer(1, 24))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GREY))
    story.append(Spacer(1, 6))
    story.append(Paragraph(_footer_text(clinic_info), styles["Footer"]))

    doc.build(story)
    return buf.getvalue()


# ─── Factura Electrónica (e-CF) ────────────────────────────────────────────────

def generate_invoice_pdf(invoice: dict, clinic_info: dict) -> bytes:
    """Genera la representación impresa en PDF de una factura e-CF."""
    buf = io.BytesIO()
    # Margen estrecho para diseño de factura limpia
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    styles = _base_styles()
    story = []

    # Estilos de factura personalizados
    styles.add(ParagraphStyle(
        name="InvoiceClinicTitle",
        fontSize=16,
        fontName="Helvetica-Bold",
        textColor=BLACK,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="InvoiceTypeTitle",
        fontSize=11,
        fontName="Helvetica-Bold",
        textColor=BLACK,
        alignment=TA_RIGHT,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="InvoiceRightBold",
        fontSize=12,
        fontName="Helvetica-Bold",
        textColor=BLACK,
        alignment=TA_RIGHT,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="InvoiceRightText",
        fontSize=9,
        fontName="Helvetica",
        textColor=BLACK,
        alignment=TA_RIGHT,
    ))
    styles.add(ParagraphStyle(
        name="InvoiceLeftText",
        fontSize=9,
        fontName="Helvetica",
        textColor=BLACK,
        leading=13,
    ))
    styles.add(ParagraphStyle(
        name="InvoiceTableHeader",
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=BLACK,
        alignment=TA_CENTER,
    ))

    # --- CABECERA DE FACTURA ---
    # Lado Izquierdo: Datos de la Clínica
    clinic_name = clinic_info.get("clinic_name", "Consultorio Médico")
    clinic_addr = clinic_info.get("clinic_address", "")
    clinic_tel = clinic_info.get("clinic_phone", "")
    clinic_email = clinic_info.get("clinic_email", "")
    clinic_rnc = clinic_info.get("clinic_rnc", "")
    created_at = invoice.get("created_at") or datetime.now().strftime("%d-%m-%Y")
    
    left_lines = [
        f"<b>{clinic_name}</b>",
        clinic_name,
    ]
    if clinic_rnc:
        left_lines.append(f"<b>RNC:</b> {clinic_rnc}")
    if clinic_addr:
        left_lines.append(f"<b>Dirección:</b> {clinic_addr}")
    if clinic_tel:
        left_lines.append(f"<b>Teléfono:</b> {clinic_tel}")
    if clinic_email:
        left_lines.append(f"<b>Correo:</b> {clinic_email}")
    left_lines.append(f"<b>Fecha de Emisión:</b> {created_at}")
    
    left_p = Paragraph("<br/>".join(left_lines), styles["InvoiceLeftText"])

    # Lado Derecho: Datos del Comprobante
    tipo_ecf = invoice.get("tipo_ecf") or "E32"
    if tipo_ecf == "E31":
        doc_title = "FACTURA DE CRÉDITO FISCAL ELECTRÓNICA"
    else:
        doc_title = "FACTURA DE CONSUMO ELECTRÓNICA"
        
    encf = invoice.get("encf") or "—"
    # Fecha de vencimiento a 2 años o fija al 31-12-2028 como en la imagen
    vencimiento = "31-12-2028"

    right_lines = [
        f"<b>{doc_title}</b>",
        f'<font size="13"><b>{encf}</b></font>',
        f"<b>Vencimiento:</b> {vencimiento}"
    ]
    right_p = Paragraph("<br/>".join(right_lines), styles["InvoiceRightText"])

    header_table = Table([[left_p, right_p]], colWidths=["50%", "50%"])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceBefore=4, spaceAfter=8))

    # --- DATOS DEL CLIENTE ---
    client_name = invoice.get("patient_name") or "Consumidor Final"
    client_cedula = invoice.get("patient_cedula") or "—"
    payment_method_str = (invoice.get("payment_method") or "Efectivo").capitalize()
    
    client_left = [
        f"<b>Cliente:</b> {client_name}",
        f"<b>RNC/Cédula:</b> {client_cedula}"
    ]
    client_right = [
        f"<b>Tipo de Pago:</b> {payment_method_str}"
    ]
    
    c_left_p = Paragraph("<br/>".join(client_left), styles["InvoiceLeftText"])
    c_right_p = Paragraph("<br/>".join(client_right), styles["InvoiceLeftText"])
    
    client_table = Table([[c_left_p, c_right_p]], colWidths=["60%", "40%"])
    client_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(client_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.black, spaceBefore=4, spaceAfter=8))

    # --- TABLA DE ITEMS ---
    # Cantidad | Descripción | Precio | ITBIS | Total
    header = [
        Paragraph("<b>CANTIDAD</b>", styles["InvoiceTableHeader"]),
        Paragraph("<b>DESCRIPCIÓN</b>", styles["InvoiceTableHeader"]),
        Paragraph("<b>PRECIO</b>", styles["InvoiceTableHeader"]),
        Paragraph("<b>ITBIS</b>", styles["InvoiceTableHeader"]),
        Paragraph("<b>TOTAL</b>", styles["InvoiceTableHeader"]),
    ]
    
    # Cálculos de precio/itbis/total
    total = invoice.get("total") or 3000.0
    itbis = invoice.get("itbis") or 0.0
    amount = invoice.get("amount") or (total - itbis)
    
    # En el detalle, el TOTAL del ítem es el precio base en e-CF, luego se sumará el ITBIS al final.
    # En el comprobante original E31 el total del ítem es 2,542.37.
    # En E32 el total del ítem es 3,000.00.
    item_total = amount
    
    row_data = [
        Paragraph("1", styles["InvoiceTableHeader"]),
        Paragraph("Consulta Medica General", styles["InvoiceLeftText"]),
        Paragraph(f"{amount:,.2f}", ParagraphStyle("Right", parent=styles["InvoiceLeftText"], alignment=TA_RIGHT)),
        Paragraph(f"{itbis:,.2f}", ParagraphStyle("Right", parent=styles["InvoiceLeftText"], alignment=TA_RIGHT)),
        Paragraph(f"<b>{item_total:,.2f}</b>", ParagraphStyle("Right", parent=styles["InvoiceLeftText"], alignment=TA_RIGHT)),
    ]
    
    items_table = Table([header, row_data], colWidths=["12%", "48%", "13%", "13%", "14%"])
    items_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(items_table)
    
    # Cantidad total al pie de la tabla
    story.append(Spacer(1, 4))
    story.append(Paragraph("Cantidad Total: 1.00", ParagraphStyle("QtyTotal", fontSize=8, fontName="Helvetica", textColor=colors.HexColor("#64748b"), alignment=TA_RIGHT)))
    story.append(Spacer(1, 8))

    # --- QR Y TOTALES ---
    # Generar QR
    dgii_url = invoice.get("dgii_url") or f"https://ecf.dgii.gov.do/ConsultaTimbre?encf={encf}"
    
    # Widget de QR en ReportLab
    qr_code = qr.QrCodeWidget(dgii_url)
    bounds = qr_code.getBounds()
    qr_w = bounds[2] - bounds[0]
    qr_h = bounds[3] - bounds[1]
    qr_size = 90
    qr_drawing = Drawing(qr_size, qr_size, transform=[qr_size/qr_w, 0, 0, qr_size/qr_h, 0, 0])
    qr_drawing.add(qr_code)
    
    # Textos bajo el QR
    seg_code = invoice.get("codigo_seguridad") or "—"
    qr_text_lines = [
        f"<b>Código de Seguridad:</b> {seg_code}",
        f"<b>Fecha Firma Digital:</b> {created_at}"
    ]
    qr_desc_p = Paragraph("<br/>".join(qr_text_lines), styles["InvoiceLeftText"])
    
    # Celda izquierda con QR y su detalle
    qr_cell = [
        qr_drawing,
        Spacer(1, 6),
        qr_desc_p
    ]
    
    # Celda derecha con los Totales
    subtotal_gravado = amount if itbis > 0 else 0.0
    monto_exento = amount if itbis == 0 else 0.0
    
    totales_rows = [
        [Paragraph("Subtotal Gravado", styles["InvoiceLeftText"]), Paragraph(f"{subtotal_gravado:,.2f}", ParagraphStyle("Right", parent=styles["InvoiceLeftText"], alignment=TA_RIGHT))],
        [Paragraph("Monto Exento", styles["InvoiceLeftText"]), Paragraph(f"{monto_exento:,.2f}", ParagraphStyle("Right", parent=styles["InvoiceLeftText"], alignment=TA_RIGHT))],
        [Paragraph(f"ITBIS (18%)", styles["InvoiceLeftText"]), Paragraph(f"{itbis:,.2f}", ParagraphStyle("Right", parent=styles["InvoiceLeftText"], alignment=TA_RIGHT))],
        [Paragraph("<b>TOTAL</b>", ParagraphStyle("TotalText", fontSize=12, fontName="Helvetica-Bold")), Paragraph(f"<b>{total:,.2f}</b>", ParagraphStyle("TotalVal", fontSize=12, fontName="Helvetica-Bold", alignment=TA_RIGHT))],
    ]
    
    amount_paid = invoice.get("amount_paid")
    balance_due = invoice.get("balance_due")
    
    totales_style = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 2), (1, 2), 1.5, colors.black), # Línea gruesa antes del total
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]
    
    # Si hay cobro parcial
    if balance_due is not None and amount_paid is not None and float(balance_due) > 0:
        totales_rows.append([
            Paragraph("<b>Monto Pagado (Abono)</b>", ParagraphStyle("PaidText", fontSize=10, fontName="Helvetica-Bold", textColor=colors.HexColor("#16a34a"))),
            Paragraph(f"<b>{float(amount_paid):,.2f}</b>", ParagraphStyle("PaidVal", fontSize=10, fontName="Helvetica-Bold", textColor=colors.HexColor("#16a34a"), alignment=TA_RIGHT))
        ])
        totales_rows.append([
            Paragraph("<b>Balance Pendiente</b>", ParagraphStyle("DueText", fontSize=10, fontName="Helvetica-Bold", textColor=colors.HexColor("#dc2626"))),
            Paragraph(f"<b>{float(balance_due):,.2f}</b>", ParagraphStyle("DueVal", fontSize=10, fontName="Helvetica-Bold", textColor=colors.HexColor("#dc2626"), alignment=TA_RIGHT))
        ])
        totales_style.append(("LINEBELOW", (0, 3), (1, 3), 1, colors.HexColor("#cbd5e1")))
    
    totales_table = Table(totales_rows, colWidths=["60%", "40%"])
    totales_table.setStyle(TableStyle(totales_style))
    
    # Tabla contenedora de QR e Totales
    bottom_split_table = Table([[qr_cell, totales_table]], colWidths=["50%", "50%"])
    bottom_split_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(bottom_split_table)
    
    # --- SIGNATURES ---
    story.append(Spacer(1, 40))
    sig_rows = [
        [
            Paragraph("________________________________________", ParagraphStyle("Line", alignment=TA_CENTER)),
            Paragraph("________________________________________", ParagraphStyle("Line", alignment=TA_CENTER))
        ],
        [
            Paragraph("Autorizado Por", ParagraphStyle("SigText", fontSize=8, fontName="Helvetica", textColor=colors.HexColor("#64748b"), alignment=TA_CENTER)),
            Paragraph("Recibido Por", ParagraphStyle("SigText", fontSize=8, fontName="Helvetica", textColor=colors.HexColor("#64748b"), alignment=TA_CENTER))
        ]
    ]
    sig_table = Table(sig_rows, colWidths=["50%", "50%"])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(sig_table)

    doc.build(story)
    return buf.getvalue()

