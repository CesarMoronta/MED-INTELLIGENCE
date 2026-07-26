# -*- coding: utf-8 -*-
"""
generate_manual.py — Generador de Manual de Usuario en PDF para MED-INTELLIGENCE PRO v3.0
Utiliza ReportLab 5.0 para construir un documento PDF de alta calidad editorial.
"""

import os
import sys
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# ── CANVAS PERSONALIZADO PARA NUMERACIÓN Y ENCABEZADOS ────────────────────────
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # En la primera página (Portada/Inicio) no dibujamos encabezado superior ni pie estándar
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))

        # Encabezado superior
        self.drawString(54, 750, "MED-INTELLIGENCE PRO v3.0  |  Manual Oficial de Usuario")
        self.setFont("Helvetica", 8)
        self.drawRightString(612 - 54, 750, "Sistema de Diagnóstico e Inteligencia Clínica")
        
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(54, 742, 612 - 54, 742)

        # Pie de página
        self.line(54, 48, 612 - 54, 48)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(54, 34, "Documento Confidencial — Propiedad de MED-INTELLIGENCE")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(612 - 54, 34, page_str)
        self.restoreState()


def create_callout(text, title="NOTA IMPORTANTE", bg_color="#F0F9FF", border_color="#0284C7", title_color="#0369A1", style_body=None):
    """Crea una caja de llamada visualmente atractiva (Callout box)."""
    content = [
        Paragraph(f"<b>{title}</b>", ParagraphStyle(
            'CalloutTitle', parent=style_body, fontSize=10, leading=13, textColor=colors.HexColor(title_color)
        )),
        Spacer(1, 4),
        Paragraph(text, ParagraphStyle(
            'CalloutBody', parent=style_body, fontSize=9, leading=13, textColor=colors.HexColor("#334155")
        ))
    ]
    t = Table([[content]], colWidths=[504])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg_color)),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor(border_color)),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    return t


def build_pdf(filename="Manual_de_Usuario_MED_INTELLIGENCE_PRO.pdf"):
    pdf_path = os.path.abspath(filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados
    c_primary = colors.HexColor("#0F172A")   # Deep Slate Blue
    c_secondary = colors.HexColor("#1E40AF") # Deep Royal Blue
    c_accent = colors.HexColor("#0284C7")    # Teal Blue
    c_body = colors.HexColor("#334155")      # Dark Slate Gray

    title_style = ParagraphStyle(
        'CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_accent,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_secondary,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_body,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_body,
        leftIndent=12,
        spaceAfter=3
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=0
    )

    table_body_style = ParagraphStyle(
        'TableBody',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=c_body
    )

    story = []

    # ── BANNER DE PORTADA ────────────────────────────────────────────────────────
    story.append(Spacer(1, 10))
    
    # Header box visual
    header_data = [
        [
            Paragraph("<b>MED-INTELLIGENCE PRO</b> v3.0", ParagraphStyle('BannerMain', fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=colors.white)),
            Paragraph("<b>MANUAL OFICIAL DE USUARIO</b>", ParagraphStyle('BannerSub', fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.HexColor("#93C5FD"), alignment=2))
        ],
        [
            Paragraph("Plataforma Clínica Integral de Diagnóstico Bayesiano & Asistencia por IA Generativa", ParagraphStyle('BannerTag', fontName='Helvetica', fontSize=10, leading=13, textColor=colors.HexColor("#E0F2FE"))),
            Paragraph("Versión del Sistema: 3.0 (2026)", ParagraphStyle('BannerDate', fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor("#BAE6FD"), alignment=2))
        ]
    ]
    banner_table = Table(header_data, colWidths=[340, 164])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_primary),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 16),
        ('RIGHTPADDING', (0,0), (-1,-1), 16),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 15))

    # Cuadro Resumen Informativo
    meta_box_data = [
        [
            Paragraph("<b>Documento:</b> Manual Operativo y Guía de Usuario", body_style),
            Paragraph("<b>Público Objetivo:</b> Médicos, Secretarias, Administradores", body_style)
        ],
        [
            Paragraph("<b>Motor Clínico:</b> Bayesiano 23 Enfermedades + Gemini 2.5 Flash", body_style),
            Paragraph("<b>Región / Normativa:</b> República Dominicana (JCE / NCF / ARS)", body_style)
        ]
    ]
    meta_table = Table(meta_box_data, colWidths=[250, 254])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # ── TABLA DE CONTENIDOS ──────────────────────────────────────────────────────
    story.append(Paragraph("Índice de Contenidos", h2_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    toc_items = [
        ("1. Visión General y Arquitectura del Sistema", "Pág. 2"),
        ("2. Autenticación, Seguridad y Configuración de Perfil Médico", "Pág. 2"),
        ("3. Panel de Control (Dashboard) y Centro de Notificaciones", "Pág. 3"),
        ("4. Gestión Integral de Pacientes y Consulta JCE (RD)", "Pág. 3"),
        ("5. Agenda de Citas y Control de Estado de Pacientes", "Pág. 4"),
        ("6. Registro de Consulta y Monitor de Signos Vitales (SOAPI)", "Pág. 4"),
        ("7. Motor de Diagnóstico Inteligente Bayesiano + Gemini 2.5 Flash", "Pág. 5"),
        ("8. Generación Asistida de Recetas Médicas Inteligentes", "Pág. 6"),
        ("9. Módulo de Facturación, Comprobantes NCF y Seguros ARS", "Pág. 6"),
        ("10. Expediente Documental y Adjuntos Radiológicos/Laboratorio", "Pág. 7"),
        ("11. Bot Médico de Telegram para Telemedicina", "Pág. 7"),
        ("12. Impresión de Documentos Oficiales en PDF y Reportes", "Pág. 8")
    ]
    toc_table_data = []
    for section, page in toc_items:
        toc_table_data.append([
            Paragraph(f"• {section}", ParagraphStyle('TOCItem', fontName='Helvetica', fontSize=9, leading=12, textColor=c_primary)),
            Paragraph(f"<b>{page}</b>", ParagraphStyle('TOCPage', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=c_secondary, alignment=2))
        ])
    toc_table = Table(toc_table_data, colWidths=[420, 84])
    toc_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(toc_table)
    story.append(Spacer(1, 15))

    # Callout de inicio
    story.append(create_callout(
        "Este manual describe el funcionamiento integral de <b>MED-INTELLIGENCE PRO v3.0</b>. Se recomienda a todo profesional de la salud y personal administrativo revisar las secciones correspondientes a su perfil antes de operar el sistema.",
        title="BIENVENIDO A MED-INTELLIGENCE PRO", bg_color="#EFF6FF", border_color="#3B82F6", title_color="#1D4ED8", style_body=body_style
    ))

    # Page break a contenido detallado
    story.append(PageBreak())

    # ── CAPÍTULO 1: VISIÓN GENERAL ───────────────────────────────────────────────
    story.append(Paragraph("1. Visión General y Arquitectura del Sistema", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "<b>MED-INTELLIGENCE PRO v3.0</b> es un ecosistema médico de alta precisión diseñado para optimizar el flujo de trabajo clínico, la gestión de expedientes y la toma de decisiones diagnósticas en centros médicos, clínicas y consultorios independientes.",
        body_style
    ))
    story.append(Paragraph(
        "La plataforma integra un <b>Motor Probabilístico Bayesiano local</b> entrenado sobre 23 condiciones clínico-respiratorias y metabólicas de alta prevalencia, potenciado sincrónicamente con <b>Inteligencia Artificial Generativa (Google Gemini 2.5 Flash)</b> para el enriquecimiento narrativo y la validación de seguridad de recetas.",
        body_style
    ))

    story.append(Paragraph("Perfiles y Roles de Usuario", h2_style))
    
    roles_data = [
        [Paragraph("Rol", table_header_style), Paragraph("Permisos Principales", table_header_style), Paragraph("Nivel de Acceso", table_header_style)],
        [
            Paragraph("<b>Médico / Doctor</b>", table_body_style),
            Paragraph("Consulta médica, evaluación bayesiana + Gemini, prescripción de recetas, registro SOAPI, carga de documentos, consulta de historial y firmas.", table_body_style),
            Paragraph("<font color='#059669'><b>Clínico Total</b></font>", table_body_style)
        ],
        [
            Paragraph("<b>Secretaria / Recepción</b>", table_body_style),
            Paragraph("Agendamiento de citas, registro de nuevos pacientes, consulta de Cédula JCE, gestión de facturación, comprobantes NCF y cobro a ARS.", table_body_style),
            Paragraph("<font color='#D97706'><b>Administrativo</b></font>", table_body_style)
        ],
        [
            Paragraph("<b>Administrador</b>", table_body_style),
            Paragraph("Gestión de usuarios y claves, configuración global del centro, plan de suscripción, auditoría de base de datos y reportes gerenciales.", table_body_style),
            Paragraph("<font color='#DC2626'><b>Control Total</b></font>", table_body_style)
        ]
    ]
    roles_table = Table(roles_data, colWidths=[110, 284, 110])
    roles_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(roles_table)
    story.append(Spacer(1, 12))

    # ── CAPÍTULO 2: AUTENTICACIÓN Y CONFIGURACIÓN ────────────────────────────────
    story.append(Paragraph("2. Autenticación, Seguridad y Configuración de Perfil", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "El acceso a la plataforma requiere autenticación mediante correo institucional o usuario y contraseña encriptada mediante algoritmos PBKDF2/SHA256 (Werkzeug Security).",
        body_style
    ))
    
    story.append(Paragraph("Pasos para el Inicio de Sesión y Seguridad:", h2_style))
    story.append(Paragraph("1. Ingrese a la URL del sistema e introduzca su usuario y contraseña.", bullet_style))
    story.append(Paragraph("2. Si es su primer acceso, diríjase a <b>Mi Cuenta</b> para actualizar su contraseña temporal.", bullet_style))
    story.append(Paragraph("3. <b>Perfil Médico (Configuración de Firma y Sello):</b> Suba su firma digital manuscrita en formato transparente (PNG/JPG) y su número de exequátur/colegiación médica. Esta información se incrustará automáticamente en todas las recetas emitidas en PDF.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(create_callout(
        "Es responsabilidad del médico facultativo mantener actualizada su firma digital y exequátur. Las recetas generadas sin firma oficial pueden carecer de validez legal ante farmacias y aseguradoras.",
        title="REQUISITO LEGAL Y SEGURIDAD", bg_color="#FFFBEB", border_color="#F59E0B", title_color="#B45309", style_body=body_style
    ))
    story.append(Spacer(1, 14))

    # ── CAPÍTULO 3: DASHBOARD ───────────────────────────────────────────────────
    story.append(Paragraph("3. Panel de Control (Dashboard) y Notificaciones", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "El <b>Dashboard Médico</b> es la pantalla principal del facultativo y ofrece un panorama operativo en tiempo real:",
        body_style
    ))
    story.append(Paragraph("• <b>Métricas Rápidas:</b> Citas de Hoy, Citas Pendientes, Citas Completadas y Citas de Mañana.", bullet_style))
    story.append(Paragraph("• <b>Calendario Dinámico de Agenda:</b> Visualización de citas programadas por hora día a día con tecnología FullCalendar. Al pulsar sobre cualquier cita se despliega el menú contextual para iniciar la consulta médica o modificar la cita.", bullet_style))
    story.append(Paragraph("• <b>Centro de Notificaciones Internas:</b> Campanilla en la barra superior con badge de conteo en tiempo real. Notifica solicitudes de recepción, confirmaciones de citas y mensajes de soporte.", bullet_style))
    
    story.append(Spacer(1, 14))

    # ── CAPÍTULO 4: GESTIÓN DE PACIENTES ─────────────────────────────────────────
    story.append(Paragraph("4. Gestión Integral de Pacientes y Consulta JCE (RD)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "El módulo de Pacientes permite administrar el expediente clínico único de cada persona con soporte especial para la legislación de República Dominicana.",
        body_style
    ))
    
    story.append(Paragraph("Funcionalidades Clave del Módulo de Pacientes:", h2_style))
    story.append(Paragraph("• <b>Búsqueda Instantánea:</b> Filtrado dinámico por nombre, apellido, teléfono o número de Cédula de Identidad.", bullet_style))
    story.append(Paragraph("• <b>Integración Automatizada con Cédula JCE (RD):</b> Al ingresar el número de cédula (11 dígitos) y hacer clic en 'Consultar JCE', el sistema conecta de forma transparente con los padrones oficiales de República Dominicana y autocompleta: Nombres, Apellidos, Fecha de Nacimiento, Sexo y Foto Oficial.", bullet_style))
    story.append(Paragraph("• <b>Expediente Clínico Digital:</b> Registro exhaustivo de antecedentes patológicos personales, antecedentes quirúrgicos, alergias medicamentosas, hábitos tóxicos y antecedentes familiares.", bullet_style))
    story.append(Paragraph("• <b>Acceso Directo a Historia Clínica:</b> Visualización cronológica de todas las visitas pasadas, diagnósticos bayesianos previos, medicamentos recetados y documentos adjuntos.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(create_callout(
        "La consulta de cédula JCE requiere conexión activa a internet. En caso de caída del servicio de la JCE, los datos pueden ingresarse manualmente sin interrumpir la atención del paciente.",
        title="CONSEJO OPERATIVO JCE", bg_color="#F0FDF4", border_color="#10B981", title_color="#047857", style_body=body_style
    ))

    story.append(PageBreak())

    # ── CAPÍTULO 5: AGENDA Y CITAS ───────────────────────────────────────────────
    story.append(Paragraph("5. Agenda de Citas y Control de Pacientes", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "El flujo de agendamiento conecta el trabajo de recepción con la atención en el consultorio médico.",
        body_style
    ))
    story.append(Paragraph("<b>Pasos para Registrar una Nueva Cita:</b>", h2_style))
    story.append(Paragraph("1. Diríjase a la sección <b>Agenda / Citas</b> y pulse el botón <b>+ Agendar Cita</b>.", bullet_style))
    story.append(Paragraph("2. Seleccione el paciente existente o cree uno rápidamente desde el formulario modal.", bullet_style))
    story.append(Paragraph("3. Defina la fecha, hora de inicio, motivo de la consulta y el médico tratante.", bullet_style))
    story.append(Paragraph("4. La cita cambiará dinámicamente de estado:", bullet_style))
    story.append(Paragraph("   - <font color='#2563EB'><b>PENDIENTE:</b></font> Cita programada a la espera de llegada del paciente.", ParagraphStyle('IndentBullet', parent=bullet_style, leftIndent=24)))
    story.append(Paragraph("   - <font color='#059669'><b>ATENDIDA:</b></font> El médico completó la consulta clínica y diagnóstico.", ParagraphStyle('IndentBullet2', parent=bullet_style, leftIndent=24)))
    story.append(Paragraph("   - <font color='#DC2626'><b>CANCELADA:</b></font> El paciente o centro canceló la cita agendada.", ParagraphStyle('IndentBullet3', parent=bullet_style, leftIndent=24)))

    story.append(Spacer(1, 12))

    # ── CAPÍTULO 6: SIGNO VITALES Y SOAPI ────────────────────────────────────────
    story.append(Paragraph("6. Registro de Consulta y Monitor de Signos Vitales", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "Al iniciar una consulta médica, el sistema solicita el registro obligatorio o facultativo de los parámetros hemodinámicos y antropométricos del paciente.",
        body_style
    ))

    story.append(Paragraph("Matriz de Constantes Vitales y Alertas Automatizadas:", h2_style))

    vitals_data = [
        [Paragraph("Constante Vital", table_header_style), Paragraph("Rango Normal Estándar", table_header_style), Paragraph("Comportamiento / Alerta del Sistema", table_header_style)],
        [
            Paragraph("<b>Presión Arterial (PA)</b>", table_body_style),
            Paragraph("120 / 80 mmHg", table_body_style),
            Paragraph("Calcula autom. Presión Arterial Media (PAM). Alerta visual si PAS ≥140 o PAD ≥90 (Hipertensión) o PAS ≤90 (Hipotensión).", table_body_style)
        ],
        [
            Paragraph("<b>Frecuencia Cardíaca (FC)</b>", table_body_style),
            Paragraph("60 - 100 lpm", table_body_style),
            Paragraph("Alerta si &lt;60 lpm (Bradicardia) o &gt;100 lpm (Taquicardia). Alerta crítica si &gt;130 lpm.", table_body_style)
        ],
        [
            Paragraph("<b>Frecuencia Resp. (FR)</b>", table_body_style),
            Paragraph("12 - 20 rpm", table_body_style),
            Paragraph("Alerta si &gt;20 rpm (Taquipnea) o &lt;12 rpm (Bradipnea). Indicador clave en triaje bayesiano.", table_body_style)
        ],
        [
            Paragraph("<b>Temperatura (°C)</b>", table_body_style),
            Paragraph("36.5 - 37.5 °C", table_body_style),
            Paragraph("Alerta de Febrícula (&gt;37.5 °C) o Fiebre (&gt;38.0 °C). Resalta riesgo en síndromes infecciosos.", table_body_style)
        ],
        [
            Paragraph("<b>Saturación SpO2 (%)</b>", table_body_style),
            Paragraph("95% - 100%", table_body_style),
            Paragraph("<font color='#DC2626'><b>Crítico si &lt;92%:</b></font> Detona alerta de insuficiencia respiratoria y eleva automáticamente el triaje a Rojo.", table_body_style)
        ],
        [
            Paragraph("<b>Índice Masa Corp. (IMC)</b>", table_body_style),
            Paragraph("18.5 - 24.9 kg/m²", table_body_style),
            Paragraph("Calculado automáticamente a partir de Peso (kg) y Talla (cm). Clasifica: Bajo peso, Normal, Sobrepeso, Obesidad I-III.", table_body_style)
        ]
    ]
    vitals_table = Table(vitals_data, colWidths=[120, 114, 270])
    vitals_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(vitals_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Evolución Clínica en Formato SOAPI:", h2_style))
    story.append(Paragraph("• <b>[S] Subjetivo:</b> Historia narrativa expresada por el paciente, tiempo de evolución y motivo principal.", bullet_style))
    story.append(Paragraph("• <b>[O] Objetivo:</b> Hallazgos al examen físico, auscultación, inspección y constantes vitales.", bullet_style))
    story.append(Paragraph("• <b>[A] Análisis:</b> Integración bayesiana, juicio clínico y diagnóstico diferencial.", bullet_style))
    story.append(Paragraph("• <b>[P] Plan:</b> Tratamiento farmacológico, recomendaciones, estudios indicados y cita de seguimiento.", bullet_style))

    story.append(Spacer(1, 14))

    # ── CAPÍTULO 7: MOTOR DIAGNÓSTICO BAYESIANO E IA ─────────────────────────────
    story.append(Paragraph("7. Motor Diagnóstico Bayesiano e IA Gemini 2.5 Flash", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "El núcleo de inteligencia de <b>MED-INTELLIGENCE PRO</b> combina dos algoritmos avanzados que trabajan en sinergia:",
        body_style
    ))

    story.append(Paragraph("1. Motor Probabilístico Bayesiano (Algoritmo Local)", h2_style))
    story.append(Paragraph(
        "Calcula la probabilidad posterior P(Enfermedad | Síntomas) aplicando el Teorema de Bayes sobre Likelihood Ratios (LR+ y LR-) validados en literatura médica. Evalúa 23 patologías estándar divididas en tres niveles de triaje:",
        body_style
    ))

    triage_data = [
        [Paragraph("Nivel Triaje", table_header_style), Paragraph("Color / Código", table_header_style), Paragraph("Patologías Evaluadas (Ejemplos)", table_header_style), Paragraph("Acción Clínica Recomendada", table_header_style)],
        [
            Paragraph("<b>Nivel Verde</b><br/>Bajo Riesgo", table_body_style),
            Paragraph("<font color='#10B981'><b>VERDE</b></font>", table_body_style),
            Paragraph("Gripe Común, Bronquitis Aguda, Rinitis, Sinusitis Aguda, Faringoamigdalitis, ERGE.", table_body_style),
            Paragraph("Manejo ambulatorio con tratamiento sintomático y reposo.", table_body_style)
        ],
        [
            Paragraph("<b>Nivel Amarillo</b><br/>Riesgo Moderado", table_body_style),
            Paragraph("<font color='#F59E0B'><b>AMARILLO</b></font>", table_body_style),
            Paragraph("Neumonía Comunitaria, Crisis Asmática Aguda, EPOC Exacerbado, Dengue, IVU.", table_body_style),
            Paragraph("Atención prioritaria, requerimiento de antibióticos/estudios RX.", table_body_style)
        ],
        [
            Paragraph("<b>Nivel Rojo</b><br/>Emergencia / Crítico", table_body_style),
            Paragraph("<font color='#DC2626'><b>ROJO</b></font>", table_body_style),
            Paragraph("Infarto Agudo Miocardio (IAM), ACV, Tromboembolismo Pulmonar, Miocarditis, COVID Grave.", table_body_style),
            Paragraph("<font color='#DC2626'><b>Derivación inmediata a sala de urgencias / UCI.</b></font>", table_body_style)
        ]
    ]
    triage_table = Table(triage_data, colWidths=[90, 80, 194, 140])
    triage_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(triage_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("2. Capa de Enriquecimiento Narrativo con IA Gemini 2.5 Flash", h2_style))
    story.append(Paragraph(
        "Al finalizar la evaluación de síntomas, el motor envía el perfil clínico a <b>Google Gemini 2.5 Flash</b> (mediante la librería `google-genai` con respaldo OpenRouter), produciendo un análisis estructurado (Pydantic Schema) que incluye:",
        body_style
    ))
    story.append(Paragraph("• <b>Validación Clínica Coherente:</b> Comentario médico narrativo sobre la concordancia entre síntomas y constantes vitales.", bullet_style))
    story.append(Paragraph("• <b>Síntomas Sugeridos a Explorar:</b> Propone hasta 4 síntomas adicionales para hacer diagnóstico diferencial.", bullet_style))
    story.append(Paragraph("• <b>Alertas de Riesgo Clínico:</b> Identificación de signos de alarma inadvertidos.", bullet_style))
    story.append(Paragraph("• <b>Ajuste Fino Diagnóstico:</b> Si la IA considera que existe una entidad clínica más probable que la probabilidad bayesiana pura, propone el ajuste justificado.", bullet_style))

    story.append(PageBreak())

    # ── CAPÍTULO 8: RECETAS INTELIGENTES ─────────────────────────────────────────
    story.append(Paragraph("8. Generación Asistida de Recetas Médicas Inteligentes", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "El módulo de prescripción cuenta con un asistente inteligente accionado por IA que analiza el diagnóstico confirmado y las constantes vitales del paciente para formular la indicación recomendada.",
        body_style
    ))

    story.append(Paragraph("Reglas de Seguridad Algorítmica en Recetas:", h2_style))
    story.append(Paragraph("1. <b>Filtro de Emergencia (Triaje Rojo):</b> Si el paciente presenta un nivel de triaje Rojo o signos inestables, el asistente restringe la prescripción a únicamente alivio sintomático básico de soporte (ej. Paracetamol) y alerta al médico de la necesidad de transferir a urgencias.", bullet_style))
    story.append(Paragraph("2. <b>Dosificación Estándar Ambulatoria:</b> Para triajes Verde o Amarillo, genera los medicamentos de primera línea validados especificados con: Nombre y concentración, Dosis por toma, Frecuencia horaria, Duración en días y Cantidad total de cajas o unidades a dispensar.", bullet_style))
    story.append(Paragraph("3. <b>Edición y Validación Final por el Médico:</b> El médico mantiene en todo momento el control absoluto. Puede editar, agregar o eliminar fármacos del listado sugerido antes de guardar y firmar la receta.", bullet_style))

    story.append(Spacer(1, 14))

    # ── CAPÍTULO 9: FACTURACIÓN Y NCF/ARS ────────────────────────────────────────
    story.append(Paragraph("9. Facturación, Comprobantes NCF y Seguros ARS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "El módulo de facturación está diseñado para cumplir con la normativa fiscal de la <b>Dirección General de Impuestos Internos (DGII) de República Dominicana</b> y gestionar reclamos a Aseguradoras de Riesgos de Salud (ARS).",
        body_style
    ))

    story.append(Paragraph("Tipos de Comprobantes Fiscales (NCF) Soportados:", h2_style))

    ncf_data = [
        [Paragraph("Tipo NCF / Código", table_header_style), Paragraph("Denominación Fiscal", table_header_style), Paragraph("Uso / Destinatario", table_header_style)],
        [
            Paragraph("<b>B01</b>", table_body_style),
            Paragraph("Crédito Fiscal", table_body_style),
            Paragraph("Facturación a empresas o personas jurídicas que requieren deducir ITBIS / Gastos de ISR.", table_body_style)
        ],
        [
            Paragraph("<b>B02</b>", table_body_style),
            Paragraph("Consumidor Final", table_body_style),
            Paragraph("Facturación habitual a pacientes particulares que no requieren crédito fiscal.", table_body_style)
        ],
        [
            Paragraph("<b>B14</b>", table_body_style),
            Paragraph("Regímenes Especiales", table_body_style),
            Paragraph("Pacientes amparados por regímenes de exención fiscal o zonas francas.", table_body_style)
        ],
        [
            Paragraph("<b>B15</b>", table_body_style),
            Paragraph("Gubernamental", table_body_style),
            Paragraph("Facturación emitida a instituciones del Estado Dominicano.", table_body_style)
        ]
    ]
    ncf_table = Table(ncf_data, colWidths=[80, 144, 280])
    ncf_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(ncf_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Gestión de Seguros de Salud (ARS) y Copagos:", h2_style))
    story.append(Paragraph("• <b>Selección de ARS:</b> Soporta catálogos de ARS Humano, Primera ARS, SeNaSa (Régimen Contributivo/Subsidiado), ARS Palic/Mapfre, Monumental, entre otras.", bullet_style))
    story.append(Paragraph("• <b>Cálculo Automático de Copago:</b> Al ingresar el monto bruto del procedimiento o consulta y el porcentaje de cobertura acordado con la ARS, el sistema calcula automáticamente la diferencia neta (Copago) a cobrar al paciente en caja.", bullet_style))

    story.append(Spacer(1, 14))

    # ── CAPÍTULO 10: EXPEDIENTE DOCUMENTAL ───────────────────────────────────────
    story.append(Paragraph("10. Expediente Documental y Adjuntos Radiológicos", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "El módulo de Documentos Clínicos (`routes/documents.py`) permite cargar, categorizar y visualizar estudios complementarios vinculados al expediente del paciente:",
        body_style
    ))
    story.append(Paragraph("• <b>Tipos de Archivos Admitidos:</b> Documentos PDF, imágenes en formato PNG, JPG, JPEG (estudios de laboratorio, electrocardiogramas, ultrasonidos, radiografías).", bullet_style))
    story.append(Paragraph("• <b>Límite de Tamaño y Seguridad:</b> Tamaño máximo de subida configurable (por defecto 10 MB por archivo). Los archivos son escaneados y almacenados con nombres únicos en la carpeta segura `uploads/`.", bullet_style))
    story.append(Paragraph("• <b>Visualizador Integrado:</b> Permite abrir y revisar estudios analíticos directamente desde la ficha del paciente durante la consulta.", bullet_style))

    story.append(Spacer(1, 14))

    # ── CAPÍTULO 11: BOT DE TELEGRAM ─────────────────────────────────────────────
    story.append(Paragraph("11. Bot Médico de Telegram y Telemedicina", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "<b>MED-INTELLIGENCE PRO v3.0</b> incorpora un Bot de Telegram interactivo (`routes/telegram_bot.py`) para asistencia remota y notificaciones al médico tratante.",
        body_style
    ))
    story.append(Paragraph("Funcionalidades del Bot de Telegram:", h2_style))
    story.append(Paragraph("1. <b>Notificaciones de Consultas:</b> Alerta al médico en su teléfono móvil cuando un paciente ha sido registrado o requiere atención urgente.", bullet_style))
    story.append(Paragraph("2. <b>Consulta Rápida de Síntomas:</b> El médico puede interactuar con el bot mediante comandos slash (`/triaje`, `/paciente`, `/receta`) para obtener orientación probabilística bayesiana de emergencia mientras se desplaza fuera del consultorio.", bullet_style))

    story.append(PageBreak())

    # ── CAPÍTULO 12: PDFS Y REPORTES ─────────────────────────────────────────────
    story.append(Paragraph("12. Impresión de Documentos Oficiales y Reportes", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "El sistema incluye un motor gráfico interno con <b>ReportLab</b> (`routes/pdf_routes.py`) capaz de renderizar al instante documentos listos para imprimir o enviar por correo electrónico:",
        body_style
    ))

    pdf_docs_data = [
        [Paragraph("Documento Generado", table_header_style), Paragraph("Contenido e Inclusiones Clave", table_header_style), Paragraph("Ruta / Endpoint", table_header_style)],
        [
            Paragraph("<b>Receta Médica Oficial (PDF)</b>", table_body_style),
            Paragraph("Encabezado de la clínica, datos completos del paciente, listado de fármacos con posología exacta, indicación de uso, fecha, firma manuscrita digitalizada y sello con exequátur del médico.", table_body_style),
            Paragraph("<code>/api/pdf/prescription/&lt;id&gt;</code>", table_body_style)
        ],
        [
            Paragraph("<b>Informe Clínico Diagnóstico (PDF)</b>", table_body_style),
            Paragraph("Resumen de la visita médica, constantes vitales tomadas, probabilidad de diagnóstico bayesiano, comentarios de la IA Gemini, semáforo de triaje y plan de manejo.", table_body_style),
            Paragraph("<code>/api/pdf/diagnostic/&lt;id&gt;</code>", table_body_style)
        ],
        [
            Paragraph("<b>Comprobante de Cobro / Factura (PDF)</b>", table_body_style),
            Paragraph("Detalle de servicios prestados, número de NCF (DGII), cobertura de seguro ARS, monto a pagar, método de pago y desglose fiscal.", table_body_style),
            Paragraph("<code>/api/pdf/invoice/&lt;id&gt;</code>", table_body_style)
        ]
    ]
    pdf_docs_table = Table(pdf_docs_data, colWidths=[130, 260, 114])
    pdf_docs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(pdf_docs_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Módulo de Reportes y Analítica Clínico-Estadística:", h2_style))
    story.append(Paragraph("A través de la pestaña <b>Reportes</b> (`routes/reports.py`), el administrador y el médico pueden visualizar gráficos dinámicos alimentados por Chart.js con:", body_style))
    story.append(Paragraph("• <b>Distribución de Diagnósticos:</b> Gráfico circular de enfermedades más frecuentes atendidas en el período.", bullet_style))
    story.append(Paragraph("• <b>Proporción por Nivel de Triaje:</b> Volumen de pacientes clasificados en Verde, Amarillo y Rojo.", bullet_style))
    story.append(Paragraph("• <b>Productividad e Ingresos:</b> Total de consultas realizadas y balance neto acumulado de facturación.", bullet_style))

    story.append(Spacer(1, 16))

    # Caja de Cierre / Soporte
    story.append(create_callout(
        "<b>MED-INTELLIGENCE PRO v3.0</b> forma parte de la nueva generación de herramientas de soporte a la decisión médica. Recuerde que la plataforma es una herramienta de asistencia y no sustituye el criterio ni el juicio clínico del profesional de la salud.<br/><br/><b>Soporte Técnico & Consultas:</b> Soporte Interno de MED-INTELLIGENCE — Email: soporte@med-intelligence.com",
        title="DECLARACIÓN DE RESPONSABILIDAD MÉDICA Y SOPORTE", bg_color="#F8FAFC", border_color="#64748B", title_color="#334155", style_body=body_style
    ))

    # Compilar el documento
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[OK] Manual PDF generado exitosamente en: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    build_pdf()
