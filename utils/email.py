import os
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Cargar configuraciones de SMTP desde el entorno
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.environ.get("SMTP_FROM_EMAIL", "no-reply@medintelligence.com")

def _send_email_async(to_email: str, subject: str, html_body: str):
    """Función interna que realiza el envío SMTP en un hilo secundario."""
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"⚠️ SMTP no configurado. El correo para '{to_email}' no pudo enviarse.")
        print(f"Asunto: {subject}")
        print(f"Contenido: {html_body[:200]}...")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM_EMAIL
        msg["To"] = to_email

        # Adjuntar cuerpo HTML
        part = MIMEText(html_body, "html", "utf-8")
        msg.attach(part)

        # Conectar al servidor SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            if SMTP_PORT == 587:
                server.starttls()
                server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM_EMAIL, to_email, msg.as_string())
        print(f"📧 Correo enviado exitosamente a {to_email}: {subject}")
    except Exception as e:
        print(f"❌ Error al enviar correo SMTP a {to_email}: {e}")

def send_email(to_email: str, subject: str, html_body: str):
    """Envía un correo electrónico de forma asíncrona para no bloquear el request actual."""
    if not to_email:
        return
    thread = threading.Thread(target=_send_email_async, args=(to_email, subject, html_body))
    thread.daemon = True
    thread.start()
