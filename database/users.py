import json
from datetime import datetime, date
from database.connection import get_connection, get_db_cursor, rows_to_dicts, _fmt_date, MAX_LOGIN_ATTEMPTS, LOCKOUT_MINUTES
from werkzeug.security import generate_password_hash, check_password_hash

def get_user_by_username(username: str) -> dict | None:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT u.id, u.username, u.password_hash, u.role, u.full_name,
                  u.email, u.is_active, u.failed_logins, u.locked_until, u.last_login,
                  d.matricula, d.especialidad, d.telefono, d.hospital, d.id AS doctor_id,
                  u.photo_url, u.subscription_active, u.subscription_id, u.subscription_plan, u.subscription_expires_at,
                  u.cedula
           FROM dbo.users u
           LEFT JOIN dbo.doctors d ON d.user_id = u.id
           WHERE u.username = ?""",
        username
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None

    sub_active = bool(row[16])
    expires_at = row[19] # datetime object
    if not sub_active and expires_at:
        try:
            if expires_at.date() >= datetime.utcnow().date():
                sub_active = True
        except Exception:
            pass

    return {
        "id": row[0], "username": row[1], "password_hash": row[2],
        "role": row[3], "full_name": row[4], "email": row[5],
        "is_active": bool(row[6]), "failed_logins": row[7],
        "locked_until": row[8], "last_login": row[9],
        "matricula": row[10], "especialidad": row[11],
        "telefono": row[12], "hospital": row[13], "doctor_id": row[14],
        "photo_url": row[15], "subscription_active": sub_active,
        "subscription_id": row[17], "subscription_plan": row[18],
        "subscription_expires_at": _fmt_date(row[19]),
        "cedula": row[20]
    }

def get_user_by_id(user_id: int) -> dict | None:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT u.id, u.username, u.password_hash, u.role, u.full_name,
                  u.email, u.is_active, u.failed_logins, u.locked_until, u.last_login,
                  d.matricula, d.especialidad, d.telefono, d.hospital, d.id AS doctor_id,
                  u.photo_url, u.subscription_active, u.subscription_id, u.subscription_plan, u.subscription_expires_at,
                  u.cedula
           FROM dbo.users u
           LEFT JOIN dbo.doctors d ON d.user_id = u.id
           WHERE u.id = ?""",
        user_id
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        return None

    sub_active = bool(row[16])
    expires_at = row[19] # datetime object
    if not sub_active and expires_at:
        try:
            if expires_at.date() >= datetime.utcnow().date():
                sub_active = True
        except Exception:
            pass

    return {
        "id": row[0], "username": row[1], "password_hash": row[2],
        "role": row[3], "full_name": row[4], "email": row[5],
        "is_active": bool(row[6]), "failed_logins": row[7],
        "locked_until": _fmt_date(row[8]), "last_login": _fmt_date(row[9]),
        "matricula": row[10], "especialidad": row[11],
        "telefono": row[12], "hospital": row[13], "doctor_id": row[14],
        "photo_url": row[15], "subscription_active": sub_active,
        "subscription_id": row[17], "subscription_plan": row[18],
        "subscription_expires_at": _fmt_date(row[19]),
        "cedula": row[20]
    }

def verify_user(username: str, password: str, ip_address: str = None) -> dict | None:
    """
    Verifica credenciales. Registra intento y aplica bloqueo temporal.
    Retorna dict del usuario si es correcto, None si no.
    """
    user = get_user_by_username(username)

    if not user:
        _register_attempt(username, ip_address, False)
        return None

    # Verificar si está bloqueado
    if user.get("locked_until"):
        locked_until = user["locked_until"]
        if isinstance(locked_until, str):
            try:
                from datetime import timezone
                locked_until = datetime.fromisoformat(locked_until)
                if locked_until.tzinfo is None:
                    locked_until = locked_until.replace(tzinfo=timezone.utc)
                from datetime import timezone
                now = datetime.now(timezone.utc)
            except Exception:
                now = datetime.utcnow()
        else:
            now = datetime.utcnow()

        try:
            if locked_until > now:
                return None  # Cuenta bloqueada
        except Exception:
            pass

    if not user.get("is_active"):
        return None

    if not check_password_hash(user["password_hash"], password):
        _register_attempt(username, ip_address, False)
        return None

    _register_attempt(username, ip_address, True)
    return {
        "id": user["id"], "username": user["username"],
        "role": user["role"], "full_name": user.get("full_name"),
        "matricula": user.get("matricula"), "doctor_id": user.get("doctor_id"),
        "photo_url": user.get("photo_url"), "subscription_active": user.get("subscription_active"),
        "cedula": user.get("cedula")
    }

def is_account_locked(username: str) -> bool:
    """Retorna True si la cuenta está bloqueada temporalmente."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT locked_until FROM dbo.users WHERE username = ?", username
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row or row[0] is None:
        return False
    from datetime import timezone
    try:
        locked = row[0]
        now = datetime.now(timezone.utc)
        if locked.tzinfo is None:
            locked = locked.replace(tzinfo=timezone.utc)
        return locked > now
    except Exception:
        return False

def _register_attempt(username: str, ip_address: str, success: bool):
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "EXEC dbo.sp_register_login_attempt ?, ?, ?",
            username, ip_address, 1 if success else 0
        )
        cursor.close()
        conn.close()
    except Exception:
        pass

def create_user(username: str, password: str, role: str,
                full_name: str = None, email: str = None,
                matricula: str = None, especialidad: str = None,
                telefono: str = None, hospital: str = None,
                cedula: str = None, photo_url: str = None) -> dict | None:
    if get_user_by_username(username):
        return None
    pw_hash = generate_password_hash(password)
    conn    = get_connection()
    cursor  = conn.cursor()
    cursor.execute(
        "EXEC dbo.sp_create_user ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
        username, pw_hash, role, full_name, email,
        matricula, especialidad, telefono, hospital,
        cedula, photo_url
    )
    cursor.fetchone()
    cursor.close()
    conn.close()
    return get_user_by_username(username)

def update_user(user_id: int, username: str = None, password: str = None,
                role: str = None, full_name: str = None, email: str = None,
                is_active: bool = None, matricula: str = None,
                especialidad: str = None, telefono: str = None,
                hospital: str = None, cedula: str = None, photo_url: str = None) -> dict | None:
    user = get_user_by_id(user_id)
    if not user:
        return None
    pw_hash = generate_password_hash(password) if password else None
    is_active_val = None
    if is_active is not None:
        is_active_val = 1 if is_active else 0
    conn   = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "EXEC dbo.sp_update_user ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
            user_id, username, pw_hash, role, full_name, email,
            is_active_val, matricula, especialidad, telefono, hospital,
            cedula, photo_url
        )
        cursor.fetchone()
    except pyodbc.Error:
        pass
    finally:
        cursor.close()
        conn.close()
    return get_user_by_id(user_id)

def update_user_subscription(user_id: int, active: bool, sub_id: str = None, plan: str = None, expires_at = None) -> bool:
    """Actualiza la suscripción de un doctor en la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """UPDATE dbo.users
               SET subscription_active = ?,
                   subscription_id = ?,
                   subscription_plan = ?,
                   subscription_expires_at = ?
               WHERE id = ?""",
            1 if active else 0, sub_id, plan, expires_at, user_id
        )
        return True
    except Exception:
        return False
    finally:
        cursor.close()
        conn.close()

def update_user_photo(user_id: int, photo_url: str) -> bool:
    """Actualiza la foto de perfil de un usuario."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE dbo.users SET photo_url = ? WHERE id = ?",
            photo_url, user_id
        )
        return True
    except Exception:
        return False
    finally:
        cursor.close()
        conn.close()

def list_users() -> list:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, username, role, full_name, email, is_active,
                  failed_logins, locked_until, last_login, created_at,
                  matricula, especialidad, telefono, hospital, doctor_id,
                  photo_url, subscription_active, subscription_id, subscription_plan, subscription_expires_at,
                  cedula
           FROM dbo.vw_users
           ORDER BY role DESC, username ASC"""
    )
    rows = rows_to_dicts(cursor)
    cursor.close()
    conn.close()
    for r in rows:
        r["is_active"]   = bool(r.get("is_active", 1))
        r["locked_until"] = _fmt_date(r.get("locked_until"))
        r["last_login"]   = _fmt_date(r.get("last_login"))
        r["created_at"]   = _fmt_date(r.get("created_at"))
        
        sub_active = bool(r.get("subscription_active", 0))
        expires_at = r.get("subscription_expires_at") # datetime object or None
        if not sub_active and expires_at:
            try:
                if expires_at.date() >= datetime.utcnow().date():
                    sub_active = True
            except Exception:
                pass
        r["subscription_active"] = sub_active
        r["subscription_expires_at"] = _fmt_date(r.get("subscription_expires_at"))
    return rows
