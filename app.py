import os
import sys

# Forzar la codificación estándar (necesario en Windows)
if getattr(sys.stdout, 'encoding', None) and sys.stdout.encoding.lower() != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from dotenv import load_dotenv
load_dotenv(override=True)

from flask import Flask
from database import initialize_database

# Inicializar Flask
app = Flask(__name__, static_folder="static")

# Seguridad: secret_key desde variables de entorno
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-in-production")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Configuración de uploads
upload_folder = os.environ.get("UPLOAD_FOLDER", "uploads")
os.makedirs(upload_folder, exist_ok=True)
app.config["UPLOAD_FOLDER"] = upload_folder
app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("MAX_UPLOAD_MB", 10)) * 1024 * 1024

# Importar blueprints
from routes.static_routes import static_bp  
from routes.auth import auth_bp
from routes.users import users_bp
from routes.patients import patients_bp
from routes.visits import visits_bp
from routes.diagnostics import diagnostics_bp
from routes.history import history_bp
from routes.admin import admin_bp
from routes.dashboard import dashboard_bp
from routes.settings import settings_bp
from routes.appointments import appointments_bp
from routes.pdf_routes import pdf_bp
from routes.documents import documents_bp
from routes.notifications import notifications_bp
from routes.billing import billing_bp
from routes.reports import reports_bp
from routes.telegram_bot import telegram_bp
from routes.schedules import schedules_bp

# Registrar blueprints
app.register_blueprint(static_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(patients_bp)
app.register_blueprint(visits_bp)
app.register_blueprint(diagnostics_bp)
app.register_blueprint(history_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(pdf_bp)
app.register_blueprint(documents_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(telegram_bp)
app.register_blueprint(schedules_bp)

@app.teardown_appcontext
def shutdown_session(exception=None):
    from database import close_all_thread_connections
    close_all_thread_connections()

if __name__ == "__main__":
    print("Iniciando base de datos...")
    initialize_database()

    print("=====================================================")
    print("🚀 MED-INTELLIGENCE PRO v3.0")
    print("=====================================================")
    print("🌐 Servidor iniciado en http://127.0.0.1:5000")
    print("=====================================================")

    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode, port=5000)