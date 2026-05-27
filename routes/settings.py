from flask import Blueprint, request, jsonify
from database import get_clinic_name, set_clinic_name
from utils import requires_login, requires_role, get_current_user

settings_bp = Blueprint("settings_bp", __name__)

@settings_bp.route("/api/settings/clinic_name", methods=["GET"])
@requires_login
def api_get_clinic_name():
    name = get_clinic_name()
    return jsonify({"success": True, "clinic_name": name})

@settings_bp.route("/api/settings/clinic_name", methods=["POST"])
@requires_role("admin")
def api_set_clinic_name():
    data = request.json or {}
    name = data.get("clinic_name")
    if not name:
        return jsonify({"success": False, "error": "Nombre requerido."}), 400
    
    set_clinic_name(name)
    return jsonify({"success": True, "message": "Nombre del consultorio actualizado."})
