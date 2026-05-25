from flask import Blueprint, request, jsonify
from extensions import engine
from database import get_audit_logs
from utils import requires_login, requires_role

admin_bp = Blueprint("admin_bp", __name__)

@admin_bp.route("/api/parameters", methods=["GET"])
@requires_login
@requires_role("admin")
def api_get_parameters():
    return jsonify({
        "success": True,
        "priors": engine.priors
    })

@admin_bp.route("/api/parameters", methods=["POST"])
@requires_login
@requires_role("admin")
def api_save_parameters():
    data   = request.json or {}
    priors = data.get("priors")
    if not priors:
        return jsonify({"success": False, "error": "No hay parámetros para guardar."}), 400

    try:
        engine.priors.update(priors)
        engine.guardar_configuracion()
        return jsonify({"success": True, "message": "Parámetros actualizados"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/api/parameters/reset", methods=["POST"])
@requires_login
@requires_role("admin")
def api_reset_parameters():
    try:
        engine.cargar_configuracion_por_defecto()
        return jsonify({"success": True, "priors": engine.priors})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/api/audit_logs", methods=["GET"])
@requires_login
@requires_role("admin")
def api_get_audit_logs():
    return jsonify({"success": True, "logs": get_audit_logs(limit=200)})
