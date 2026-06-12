import os
from flask import Blueprint, request, jsonify
from database import (get_clinic_name, set_clinic_name,
                      get_all_clinic_settings, set_clinic_settings)
from utils import requires_login, requires_role

settings_bp = Blueprint("settings_bp", __name__)


@settings_bp.route("/api/config/paypal", methods=["GET"])
@requires_login
def api_get_paypal_config():
    return jsonify({
        "success": True,
        "client_id": os.environ.get("PAYPAL_CLIENT_ID", "sb"),
        "plan_id": os.environ.get("PAYPAL_PLAN_ID", "P-58473859YY4859604M3NNZMY")
    })



@settings_bp.route("/api/settings/clinic_name", methods=["GET"])
@requires_login
def api_get_clinic_name():
    name = get_clinic_name()
    return jsonify({"success": True, "clinic_name": name})


@settings_bp.route("/api/settings/clinic_name", methods=["POST"])
@requires_login
@requires_role("admin")
def api_set_clinic_name():
    data = request.json or {}
    name = data.get("clinic_name")
    if not name:
        return jsonify({"success": False, "error": "Nombre requerido."}), 400
    set_clinic_name(name)
    return jsonify({"success": True, "message": "Nombre del consultorio actualizado."})


@settings_bp.route("/api/settings/clinic", methods=["GET"])
@settings_bp.route("/api/settings/all", methods=["GET"])   # alias JS
@requires_login
def api_get_clinic_settings():
    """Retorna todos los ajustes del consultorio."""
    settings = get_all_clinic_settings()
    return jsonify({"success": True, "settings": settings})


@settings_bp.route("/api/settings/clinic", methods=["POST"])
@settings_bp.route("/api/settings/update", methods=["POST"])   # alias JS
@requires_login
@requires_role("admin")
def api_save_clinic_settings():
    """Guarda todos los ajustes del consultorio en batch."""
    data = request.json or {}
    # Aceptar tanto {settings: {...}} como el payload plano del JS
    settings = data.get("settings") or {k: v for k, v in data.items()}
    if not settings:
        return jsonify({"success": False, "error": "No hay ajustes para guardar."}), 400
    set_clinic_settings(settings)
    return jsonify({"success": True, "message": "Ajustes del consultorio actualizados."})
