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
    if data.get("reset"):
        try:
            engine.cargar_configuracion_por_defecto()
            return jsonify({"success": True, "priors": engine.priors})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    priors = data.get("priors")
    if not priors:
        return jsonify({"success": False, "error": "No hay parámetros para guardar."}), 400

    try:
        # Convert values to float
        priors_float = {k: float(v) for k, v in priors.items()}
        engine.priors.update(priors_float)
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
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 30, type=int)
    username = request.args.get("username", "").strip() or None
    action = request.args.get("action", "").strip() or None
    ip_address = request.args.get("ip_address", "").strip() or None
    date_start = request.args.get("date_start", "").strip() or None
    date_end = request.args.get("date_end", "").strip() or None
    entity = request.args.get("entity", "").strip() or None
    
    result = get_audit_logs(
        page=page, limit=limit,
        username=username, action=action,
        ip_address=ip_address, date_start=date_start,
        date_end=date_end, entity=entity
    )
    return jsonify({
        "success": True,
        "logs": result["logs"],
        "total": result["total_count"],
        "total_count": result["total_count"],
        "total_pages": result["total_pages"],
        "page": result["page"],
        "limit": result["limit"]
    })
