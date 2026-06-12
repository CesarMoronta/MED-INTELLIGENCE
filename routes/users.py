import os
from flask import Blueprint, request, jsonify, session, current_app
from database import (list_users, create_user, get_user_by_id, update_user, 
                      log_audit_action, update_user_subscription, update_user_photo)
from utils import requires_login, requires_role, get_current_user, get_client_ip
from utils.email import send_email

users_bp = Blueprint("users_bp", __name__)

def _sanitize_user(user: dict) -> dict:
    return {k: v for k, v in user.items() if k != "password_hash"}

@users_bp.route("/api/users", methods=["GET"])
@requires_login
@requires_role("admin", "secretaria")
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
    cedula     = (data.get("cedula") or "").strip() or None
    photo_url  = (data.get("photo_url") or "").strip() or None

    if not username or not password:
        return jsonify({"success": False, "error": "Usuario y contraseña son obligatorios."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "error": "La contraseña debe tener al menos 6 caracteres."}), 400
    if role not in ["admin", "doctor", "secretaria"]:
        return jsonify({"success": False, "error": "Rol inválido."}), 400

    user = create_user(
        username=username, password=password, role=role,
        full_name=full_name, email=email,
        matricula=matricula if role == "doctor" else None,
        especialidad=especialidad if role == "doctor" else None,
        telefono=telefono if role == "doctor" else None,
        hospital=hospital if role == "doctor" else None,
        cedula=cedula, photo_url=photo_url
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
    cedula       = (data.get("cedula") or "").strip() or None
    photo_url    = (data.get("photo_url") or "").strip() or None

    if role and role not in ["admin", "doctor", "secretaria"]:
        return jsonify({"success": False, "error": "Rol inválido."}), 400
    if password and len(password) < 6:
        return jsonify({"success": False, "error": "La contraseña debe tener al menos 6 caracteres."}), 400

    user = update_user(
        user_id, username=username, password=password, role=role,
        full_name=full_name, email=email,
        is_active=is_active, matricula=matricula,
        especialidad=especialidad, telefono=telefono, hospital=hospital,
        cedula=cedula, photo_url=photo_url
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


@users_bp.route("/api/profile", methods=["GET"])
@requires_login
def api_get_profile():
    u = get_current_user()
    user = get_user_by_id(u["id"])
    if not user:
        return jsonify({"success": False, "error": "Usuario no encontrado."}), 404
    return jsonify({"success": True, "user": _sanitize_user(user)})


@users_bp.route("/api/profile", methods=["PUT"])
@requires_login
def api_update_profile():
    u = get_current_user()
    data = request.json or {}
    
    username = (data.get("username") or "").strip() or None
    password = (data.get("password") or "").strip() or None
    full_name = (data.get("full_name") or "").strip() or None
    email = (data.get("email") or "").strip() or None
    matricula = (data.get("matricula") or "").strip() or None
    especialidad = (data.get("especialidad") or "").strip() or None
    telefono = (data.get("telefono") or "").strip() or None
    hospital = (data.get("hospital") or "").strip() or None
    cedula = (data.get("cedula") or "").strip() or None
    photo_url = (data.get("photo_url") or "").strip() or None

    if password and len(password) < 6:
        return jsonify({"success": False, "error": "La contraseña debe tener al menos 6 caracteres."}), 400

    user = update_user(
        u["id"], username=username, password=password,
        full_name=full_name, email=email,
        matricula=matricula, especialidad=especialidad,
        telefono=telefono, hospital=hospital,
        cedula=cedula, photo_url=photo_url
    )
    if user is None:
        return jsonify({"success": False, "error": "No se pudo actualizar el perfil."}), 400

    # Actualizar sesión con el nuevo nombre y rol
    session["user"]["username"] = user["username"]
    session["user"]["full_name"] = user.get("full_name")
    
    log_audit_action(
        username=u.get("username"), action="UPDATE", entity="User",
        entity_id=str(u["id"]),
        details="Usuario actualizó su propio perfil",
        ip_address=get_client_ip(), user_id=u.get("id")
    )

    # Notificar por correo
    if user.get("email"):
        subject = "Actualización de cuenta en MED-INTELLIGENCE"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f6f9; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #3b82f6;">Hola, {user.get('full_name') or user.get('username')}</h2>
                <p>Te notificamos que los datos de tu cuenta en MED-INTELLIGENCE han sido actualizados recientemente.</p>
                <p>Si no realizaste este cambio, por favor ponte en contacto de inmediato con el administrador del sistema.</p>
                <br/>
                <hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 20px 0;"/>
                <p style="font-size: 12px; color: #6b7280; text-align: center;">Este es un mensaje automático, por favor no respondas a este correo.</p>
            </div>
        </body>
        </html>
        """
        send_email(user["email"], subject, body)

    return jsonify({"success": True, "user": _sanitize_user(user)})


@users_bp.route("/api/profile/upload-photo", methods=["POST"])
@requires_login
def api_profile_upload_photo():
    if "photo" not in request.files:
        return jsonify({"success": False, "error": "No se subió ningún archivo."}), 400
    file = request.files["photo"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Archivo vacío."}), 400

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ["png", "jpg", "jpeg", "gif", "webp"]:
        return jsonify({"success": False, "error": "Formato de imagen no permitido."}), 400

    upload_dir = os.path.join(current_app.static_folder, "uploads", "profiles")
    os.makedirs(upload_dir, exist_ok=True)

    u = get_current_user()
    filename = f"profile_{u['id']}.{ext}"
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    photo_url = f"/uploads/profiles/{filename}"
    update_user_photo(u["id"], photo_url)

    # Actualizar la foto en sesión
    session["user"]["photo_url"] = photo_url
    session.modified = True

    return jsonify({"success": True, "photo_url": photo_url})


@users_bp.route("/api/subscription/paypal-approved", methods=["POST"])
@requires_login
def api_paypal_approved():
    u = get_current_user()
    data = request.json or {}
    sub_id = data.get("subscription_id")
    plan_id = data.get("plan_id", "VIP")

    if not sub_id:
        return jsonify({"success": False, "error": "ID de suscripción de PayPal requerido."}), 400

    from datetime import datetime, timedelta
    expires_at = datetime.utcnow() + timedelta(days=30)

    success = update_user_subscription(u["id"], True, sub_id, plan_id, expires_at)
    if not success:
        return jsonify({"success": False, "error": "Error al registrar la suscripción."}), 500

    # Generar factura de consumo electrónica
    from routes.billing import generate_subscription_invoice
    generate_subscription_invoice(u["id"])

    # Actualizar la sesión del usuario
    session["user"]["subscription_active"] = True
    session.modified = True

    user = get_user_by_id(u["id"])

    # Enviar correo de bienvenida a VIP
    if user.get("email"):
        subject = "¡Bienvenido a MED-INTELLIGENCE VIP! 🌟"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f6f9; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #10b981; text-align: center;">¡Felicidades por tu suscripción VIP!</h2>
                <p>Estimado(a) Dr(a). {user.get('full_name') or user.get('username')},</p>
                <p>Tu cuenta ha sido ascendida a **VIP** exitosamente. Ya tienes acceso completo a las herramientas de Inteligencia Actorial Clínica.</p>
                
                <div style="background-color: #f3f4f6; padding: 15px; border-radius: 6px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: bold; color: #374151;">Detalles del plan:</p>
                    <ul style="margin: 10px 0 0 0; padding-left: 20px; color: #4b5563;">
                        <li><strong>Plan:</strong> {plan_id} ($20 USD/mes)</li>
                        <li><strong>ID de Suscripción:</strong> {sub_id}</li>
                        <li><strong>Fecha de Renovación:</strong> {expires_at.strftime('%Y-%m-%d')}</li>
                    </ul>
                </div>

                <p>Ahora puedes utilizar el diagnóstico automatizado asistido por el modelo Bayesiano y Gemini AI durante tus consultas clínicas.</p>
                <br/>
                <hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 20px 0;"/>
                <p style="font-size: 12px; color: #6b7280; text-align: center;">MED-INTELLIGENCE — Innovando en la medicina del futuro</p>
            </div>
        </body>
        </html>
        """
        send_email(user["email"], subject, body)

    return jsonify({"success": True, "message": "Suscripción activada con éxito.", "user": _sanitize_user(user)})


@users_bp.route("/api/subscription/cancel", methods=["POST"])
@requires_login
def api_cancel_subscription():
    u = get_current_user()
    user_curr = get_user_by_id(u["id"])
    if not user_curr:
        return jsonify({"success": False, "error": "Usuario no encontrado."}), 404
        
    expires_at = user_curr.get("subscription_expires_at")
    sub_id = user_curr.get("subscription_id")

    success = update_user_subscription(u["id"], False, sub_id, "VIP (Cancelada)", expires_at)
    if not success:
        return jsonify({"success": False, "error": "Error al cancelar la suscripción."}), 500

    # Obtener el usuario actualizado para verificar si sigue activo por fecha
    user = get_user_by_id(u["id"])

    # Actualizar la sesión
    session["user"]["subscription_active"] = user.get("subscription_active", False)
    session.modified = True

    user = get_user_by_id(u["id"])

    expires_date_str = expires_at.split('T')[0] if expires_at else '—'

    # Enviar correo de cancelación
    if user.get("email"):
        subject = "Suscripción VIP Cancelada - MED-INTELLIGENCE"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f6f9; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #ef4444;">Cancelación de Suscripción VIP</h2>
                <p>Estimado(a) Dr(a). {user.get('full_name') or user.get('username')},</p>
                <p>Te confirmamos que tu suscripción VIP ha sido cancelada. Tu acceso al diagnóstico clínico con IA seguirá activo hasta el <strong>{expires_date_str}</strong>, fecha en que vencerá tu período actual y pasarás al modo de diagnóstico manual.</p>
                <p>Puedes volver a suscribirte en cualquier momento desde el panel de tu cuenta.</p>
                <br/>
                <hr style="border: 0; border-top: 1px solid #e5e7eb; margin: 20px 0;"/>
                <p style="font-size: 12px; color: #6b7280; text-align: center;">MED-INTELLIGENCE</p>
            </div>
        </body>
        </html>
        """
        send_email(user["email"], subject, body)

    return jsonify({"success": True, "message": f"Suscripción cancelada con éxito. Tu acceso VIP seguirá activo hasta el {expires_date_str}.", "user": _sanitize_user(user)})


@users_bp.route("/api/subscription/send-test-email", methods=["POST"])
@requires_login
def api_send_test_email():
    u = get_current_user()
    user = get_user_by_id(u["id"])
    email = user.get("email")
    if not email:
        return jsonify({"success": False, "error": "Configura un correo electrónico en tu cuenta primero."}), 400

    subject = "Prueba de Notificación - MED-INTELLIGENCE"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Correo de Prueba Exitoso</h2>
        <p>Tu sistema de correos en MED-INTELLIGENCE está funcionando correctamente.</p>
        <p>Destinatario: {email}</p>
    </body>
    </html>
    """
    send_email(email, subject, body)
    return jsonify({"success": True, "message": f"Correo de prueba enviado a {email}."})

