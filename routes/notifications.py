from flask import Blueprint, request, jsonify
from database import (get_notifications, create_notification,
                      mark_notification_read, get_unread_count,
                      mark_all_notifications_read, list_users)
from utils import requires_login, get_current_user

notifications_bp = Blueprint("notifications_bp", __name__)


@notifications_bp.route("/api/notifications", methods=["GET"])
@requires_login
def api_get_notifications():
    u     = get_current_user()
    limit = request.args.get("limit", 30, type=int)
    notifs = get_notifications(user_id=u["id"], limit=limit)
    return jsonify({"success": True, "notifications": notifs})


@notifications_bp.route("/api/notifications/count", methods=["GET"])
@notifications_bp.route("/api/notifications/unread_count", methods=["GET"])   # alias JS
@requires_login
def api_notifications_count():
    u     = get_current_user()
    count = get_unread_count(user_id=u["id"])
    return jsonify({"success": True, "count": count})


@notifications_bp.route("/api/notifications", methods=["POST"])
@notifications_bp.route("/api/notifications/send", methods=["POST"])   # alias JS
@requires_login
def api_create_notification():
    u    = get_current_user()
    data = request.json or {}
    to_user_id = data.get("to_user_id")
    message    = (data.get("message") or "").strip()
    notif_type = data.get("type", "message")   # "message" | "alert" | "info"

    if not to_user_id or not message:
        return jsonify({"success": False, "error": "Destinatario y mensaje son requeridos."}), 400

    notif_id = create_notification(
        from_user_id = u["id"],
        to_user_id   = int(to_user_id),
        message      = message,
        notif_type   = notif_type
    )
    return jsonify({"success": True, "notification_id": notif_id})


@notifications_bp.route("/api/notifications/<int:notif_id>/read", methods=["POST"])
@requires_login
def api_mark_read(notif_id):
    mark_notification_read(notif_id)
    return jsonify({"success": True})


@notifications_bp.route("/api/notifications/read-all", methods=["POST"])
@notifications_bp.route("/api/notifications/mark_read", methods=["POST"])   # alias JS
@requires_login
def api_mark_all_read():
    u = get_current_user()
    mark_all_notifications_read(user_id=u["id"])
    return jsonify({"success": True})


@notifications_bp.route("/api/notifications/contacts", methods=["GET"])
@requires_login
def api_notification_contacts():
    """Lista de usuarios a los que se puede enviar notificaciones."""
    u     = get_current_user()
    users = list_users()
    # Excluir el usuario actual
    contacts = [
        {"id": usr["id"], "full_name": usr["full_name"] or usr["username"], "role": usr["role"]}
        for usr in users
        if usr["id"] != u["id"] and usr.get("is_active", True)
    ]
    return jsonify({"success": True, "contacts": contacts})
