"""auth_helpers.py — Decoradores y helpers de autenticación/autorización."""
from functools import wraps
from flask import session, jsonify, request


def requires_login(f):
    """Verifica que el usuario esté autenticado."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return jsonify({"success": False, "error": "Autenticación requerida."}), 401
        return f(*args, **kwargs)
    return wrapped


def requires_role(*roles):
    """Acepta uno o más roles válidos. También verifica autenticación."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user" not in session:
                return jsonify({"success": False, "error": "Autenticación requerida."}), 401
            if session["user"].get("role") not in roles:
                return jsonify({"success": False, "error": "Permiso denegado."}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator


def get_current_user() -> dict:
    return session.get("user", {})


def get_client_ip() -> str:
    return request.remote_addr or "unknown"


def format_cedula(cedula: str) -> str:
    """Asegura el formato XXX-XXXXXXX-X para la cédula dominicana."""
    if not cedula:
        return cedula
    clean = cedula.replace("-", "").replace(" ", "")
    if len(clean) == 11 and clean.isdigit():
        return f"{clean[:3]}-{clean[3:10]}-{clean[10]}"
    return cedula
