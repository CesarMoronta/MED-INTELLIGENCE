from flask import Blueprint, request, jsonify, session
from database import is_account_locked, verify_user, log_audit_action
from utils import requires_login, get_client_ip, get_current_user

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/api/auth/login", methods=["POST"])
def api_login():
    data     = request.json or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    ip       = get_client_ip()

    if not username or not password:
        return jsonify({"success": False, "error": "Usuario y contraseña son requeridos."}), 400

    if is_account_locked(username):
        return jsonify({
            "success": False,
            "error": "Cuenta bloqueada temporalmente por múltiples intentos fallidos. Intente nuevamente en 15 minutos.",
            "locked": True
        }), 429

    user = verify_user(username, password, ip_address=ip)
    if not user:
        locked = is_account_locked(username)
        return jsonify({
            "success": False,
            "error": "Cuenta bloqueada. Intente en 15 minutos." if locked else "Usuario o contraseña incorrectos.",
            "locked": locked
        }), 401

    session["user"] = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "full_name": user.get("full_name"),
        "doctor_id": user.get("doctor_id")
    }
    session.permanent = True

    log_audit_action(
        username=username, action="LOGIN", entity="Session",
        entity_id=str(user["id"]), ip_address=ip, user_id=user["id"]
    )

    return jsonify({"success": True, "user": session["user"]})

@auth_bp.route("/api/auth/logout", methods=["POST"])
@requires_login
def api_logout():
    u = get_current_user()
    log_audit_action(
        username=u.get("username"), action="LOGOUT", entity="Session",
        entity_id=str(u.get("id")), ip_address=get_client_ip(),
        user_id=u.get("id")
    )
    session.pop("user", None)
    return jsonify({"success": True, "message": "Sesión cerrada."})

@auth_bp.route("/api/auth/status", methods=["GET"])
def api_auth_status():
    user = session.get("user")
    return jsonify({"success": True, "authenticated": bool(user), "user": user})
