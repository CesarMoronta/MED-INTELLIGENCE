from flask import Blueprint, send_from_directory, session, redirect, current_app

static_bp = Blueprint("static_bp", __name__)

@static_bp.route("/")
def serve_index():
    if "user" not in session:
        return redirect("/login")
    return send_from_directory(current_app.static_folder, "index.html")

@static_bp.route("/login")
def serve_login():
    if "user" in session:
        return redirect("/")
    return send_from_directory(current_app.static_folder, "login.html")

@static_bp.route("/<path:path>")
def serve_static(path):
    return send_from_directory(current_app.static_folder, path)
