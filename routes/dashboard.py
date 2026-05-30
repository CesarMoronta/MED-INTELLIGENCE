from flask import Blueprint, request, jsonify
from database import get_dashboard_stats, get_dashboard_charts
from utils import requires_login, get_current_user

dashboard_bp = Blueprint("dashboard_bp", __name__)


@dashboard_bp.route("/api/dashboard/stats", methods=["GET"])
@requires_login
def api_dashboard_stats():
    u     = get_current_user()
    role  = u.get("role")
    uid   = u.get("id")

    stats = get_dashboard_stats(user_id=uid, role=role)
    
    # Merge charts data so frontend gets everything in one call
    doctor_id = uid if role == "doctor" else None
    charts = get_dashboard_charts(doctor_id=doctor_id)
    stats.update(charts)

    return jsonify({"success": True, "stats": stats})


@dashboard_bp.route("/api/dashboard/charts", methods=["GET"])
@requires_login
def api_dashboard_charts():
    """Datos para las gráficas del dashboard de administrador."""
    u    = get_current_user()
    uid  = u.get("id")
    role = u.get("role")
    # Doctor solo ve sus propios datos en gráficas
    doctor_id = uid if role == "doctor" else None

    charts = get_dashboard_charts(doctor_id=doctor_id)
    return jsonify({"success": True, "charts": charts})
