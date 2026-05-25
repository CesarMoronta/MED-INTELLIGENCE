from flask import Blueprint, jsonify
from database import get_dashboard_stats
from utils import requires_login, get_current_user

dashboard_bp = Blueprint("dashboard_bp", __name__)

@dashboard_bp.route("/api/dashboard/stats", methods=["GET"])
@requires_login
def api_dashboard_stats():
    stats = get_dashboard_stats()
    return jsonify({"success": True, "stats": stats})
