import os
import uuid
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from database import (list_patient_documents, add_patient_document,
                      get_patient_document, delete_patient_document,
                      get_active_medications)
from utils import requires_login, get_current_user

documents_bp = Blueprint("documents_bp", __name__)

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif", "docx", "xlsx", "txt"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@documents_bp.route("/api/patients/<int:patient_id>/documents", methods=["GET"])
@requires_login
def api_list_documents(patient_id):
    docs = list_patient_documents(patient_id)
    return jsonify({"success": True, "documents": docs})

@documents_bp.route("/api/documents", methods=["GET"])
@requires_login
def api_list_documents_alias():
    patient_id = request.args.get("patient_id", type=int)
    if not patient_id:
        return jsonify({"success": False, "error": "patient_id requerido."}), 400
    docs = list_patient_documents(patient_id)
    return jsonify({"success": True, "documents": docs})

@documents_bp.route("/api/documents/prescriptions", methods=["GET"])
@requires_login
def api_list_prescriptions_alias():
    patient_id = request.args.get("patient_id", type=int)
    if not patient_id:
        return jsonify({"success": False, "error": "patient_id requerido."}), 400
    meds = get_active_medications(patient_id)
    return jsonify({"success": True, "prescriptions": meds})


@documents_bp.route("/api/patients/<int:patient_id>/documents", methods=["POST"])
@requires_login
def api_upload_document(patient_id):
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No se recibió ningún archivo."}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"success": False, "error": "Archivo inválido."}), 400

    if not _allowed_file(file.filename):
        return jsonify({"success": False,
                        "error": f"Tipo de archivo no permitido. Use: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    original_name = secure_filename(file.filename)
    ext           = original_name.rsplit(".", 1)[1].lower()
    unique_name   = f"{uuid.uuid4().hex}.{ext}"

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    patient_folder = os.path.join(upload_folder, f"patient_{patient_id}")
    os.makedirs(patient_folder, exist_ok=True)

    file_path = os.path.join(patient_folder, unique_name)
    file.save(file_path)
    file_size = os.path.getsize(file_path)

    u      = get_current_user()
    doc_id = add_patient_document(
        patient_id   = patient_id,
        filename     = unique_name,
        original_name= original_name,
        file_type    = ext.upper(),
        file_size    = file_size,
        file_path    = file_path,
        uploaded_by  = u.get("id")
    )

    return jsonify({
        "success": True,
        "document": {
            "id":            doc_id,
            "original_name": original_name,
            "file_type":     ext.upper(),
            "file_size":     file_size,
        }
    })

@documents_bp.route("/api/documents/upload", methods=["POST"])
@requires_login
def api_upload_document_alias():
    patient_id = request.form.get("patient_id", type=int)
    if not patient_id:
        return jsonify({"success": False, "error": "patient_id requerido en form data."}), 400
    return api_upload_document(patient_id)



@documents_bp.route("/api/documents/<int:doc_id>/download", methods=["GET"])
@requires_login
def api_download_document(doc_id):
    doc = get_patient_document(doc_id)
    if not doc:
        return jsonify({"success": False, "error": "Documento no encontrado."}), 404

    if not os.path.exists(doc["file_path"]):
        return jsonify({"success": False, "error": "Archivo no encontrado en disco."}), 404

    return send_file(
        doc["file_path"],
        as_attachment=True,
        download_name=doc["original_name"],
        mimetype=f"application/{doc['file_type'].lower()}"
    )


@documents_bp.route("/api/documents/<int:doc_id>", methods=["DELETE"])
@requires_login
def api_delete_document(doc_id):
    u = get_current_user()
    if u.get("role") not in ["admin", "doctor", "secretaria"]:
        return jsonify({"success": False, "error": "Permiso denegado."}), 403

    doc = get_patient_document(doc_id)
    if not doc:
        return jsonify({"success": False, "error": "Documento no encontrado."}), 404

    # Eliminar archivo del disco
    if os.path.exists(doc["file_path"]):
        os.remove(doc["file_path"])

    delete_patient_document(doc_id)
    return jsonify({"success": True, "message": "Documento eliminado."})
