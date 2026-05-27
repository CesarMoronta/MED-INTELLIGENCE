import os
import sys

# Forzar la codificación estándar (necesario en Windows)
if sys.stdout.encoding.lower() != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from database import initialize_database

# Inicializar Flask
app = Flask(__name__, static_folder="static")
app.secret_key = "clave_secreta_super_segura"

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
from routes.patient_portal import patient_portal_bp
from routes.settings import settings_bp
from routes.appointments import appointments_bp

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
app.register_blueprint(patient_portal_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(appointments_bp)

if __name__ == "__main__":
    print("Iniciando base de datos...")
    initialize_database()

    
    print("=====================================================")
    print("🚀 MED-INTELLIGENCE PRO v2.0")
    print("=====================================================")
    print("🌐 Servidor iniciado en http://127.0.0.1:5000")
    print("=====================================================")
    
    app.run(debug=True, port=5000)