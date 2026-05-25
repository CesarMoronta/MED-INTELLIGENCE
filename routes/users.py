from flask import Blueprint, request, jsonify
from database import list_users, create_user, get_user_by_id, update_user, log_audit_action
from utils import requires_login, requires_role, get_current_user, get_client_ip

users_bp = Blueprint("users_bp", __name__)

def _sanitize_user(user: dict) -> dict:
    return {k: v for k, v in user.items() if k != "password_hash"}

@users_bp.route("/api/users", methods=["GET"])
@requires_login
@requires_role("admin")
def api_list_users():
    return jsonify({"success": True, "users": list_users()})

@users_bp.route("/api/users", methods=["POST"])
@requires_login
@requires_role("admin")
def api_create_user():
    data       = request.json or {}
    username   = (data.get("username") or "").strip()
    password   = (data.get("password") or "").strip()
    role       = (data.get("role") or "doctor").strip().lower()
    full_name  = (data.get("full_name") or "").strip() or None
    email      = (data.get("email") or "").strip() or None
    matricula  = (data.get("matricula") or "").strip() or None
    especialidad = (data.get("especialidad") or "").strip() or None
    telefono   = (data.get("telefono") or "").strip() or None
    hospital   = (data.get("hospital") or "").strip() or None

    if not username or not password:
        return jsonify({"success": False, "error": "Usuario y contraseña son obligatorios."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "error": "La contraseña debe tener al menos 6 caracteres."}), 400
    if role not in ["admin", "doctor"]:
        return jsonify({"success": False, "error": "Rol inválido."}), 400

    user = create_user(
        username=username, password=password, role=role,
        full_name=full_name, email=email,
        matricula=matricula if role == "doctor" else None,
        especialidad=especialidad if role == "doctor" else None,
        telefono=telefono if role == "doctor" else None,
        hospital=hospital if role == "doctor" else None
    )
    if user is None:
        return jsonify({"success": False, "error": "El usuario ya existe."}), 409

    u = get_current_user()
    log_audit_action(
        username=u.get("username"), action="CREATE", entity="User",
        entity_id=str(user.get("id")),
        details=f"Creado usuario '{username}' con rol '{role}'",
        ip_address=get_client_ip(), user_id=u.get("id")
    )
    return jsonify({"success": True, "user": _sanitize_user(user)})

@users_bp.route("/api/users/<int:user_id>", methods=["GET"])
@requires_login
@requires_role("admin")
def api_get_user(user_id):
    user = get_user_by_id(user_id)
    if user is None:
        return jsonify({"success": False, "error": "Usuario no encontrado."}), 404
    return jsonify({"success": True, "user": _sanitize_user(user)})

@users_bp.route("/api/users/<int:user_id>", methods=["PUT"])
@requires_login
@requires_role("admin")
def api_update_user(user_id):
    data     = request.json or {}
    username = (data.get("username") or "").strip() or None
    password = (data.get("password") or "").strip() or None
    role     = (data.get("role") or "").strip().lower() or None
    full_name    = (data.get("full_name") or "").strip() or None
    email        = (data.get("email") or "").strip() or None
    is_active    = data.get("is_active")
    matricula    = (data.get("matricula") or "").strip() or None
    especialidad = (data.get("especialidad") or "").strip() or None
    telefono     = (data.get("telefono") or "").strip() or None
    hospital     = (data.get("hospital") or "").strip() or None

    if role and role not in ["admin", "doctor"]:
        return jsonify({"success": False, "error": "Rol inválido."}), 400
    if password and len(password) < 6:
        return jsonify({"success": False, "error": "La contraseña debe tener al menos 6 caracteres."}), 400

    user = update_user(
        user_id, username=username, password=password, role=role,
        full_name=full_name, email=email,
        is_active=is_active, matricula=matricula,
        especialidad=especialidad, telefono=telefono, hospital=hospital
    )
    if user is None:
        return jsonify({"success": False, "error": "No se pudo actualizar el usuario."}), 404

    u = get_current_user()
    log_audit_action(
        username=u.get("username"), action="UPDATE", entity="User",
        entity_id=str(user_id),
        details=f"Actualización de usuario ID={user_id}",
        ip_address=get_client_ip(), user_id=u.get("id")
    )
    return jsonify({"success": True, "user": _sanitize_user(user)})
