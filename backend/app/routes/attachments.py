import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Note, Attachment

attachments_bp = Blueprint("attachments", __name__)


def get_current_user_id() -> int:
    return int(get_jwt_identity())


def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]
    )


@attachments_bp.post("/notes/<int:note_id>")
@jwt_required()
def upload_attachment(note_id: int):
    user_id = get_current_user_id()
    note = Note.query.filter_by(id=note_id, owner_id=user_id).first()
    if not note:
        return jsonify({"error": "Note not found"}), 404

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    original = secure_filename(file.filename)
    ext = original.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, unique_name)
    file.save(filepath)

    attachment = Attachment(
        filename=unique_name,
        original_filename=original,
        content_type=file.content_type or "application/octet-stream",
        size=os.path.getsize(filepath),
        note_id=note.id,
    )
    db.session.add(attachment)
    db.session.commit()

    return jsonify(attachment.to_dict()), 201


@attachments_bp.get("/<int:attachment_id>/download")
@jwt_required()
def download_attachment(attachment_id: int):
    user_id = get_current_user_id()
    attachment = (
        Attachment.query.join(Note)
        .filter(Attachment.id == attachment_id, Note.owner_id == user_id)
        .first()
    )
    if not attachment:
        return jsonify({"error": "Attachment not found"}), 404

    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        attachment.filename,
        as_attachment=True,
        download_name=attachment.original_filename,
    )


@attachments_bp.delete("/<int:attachment_id>")
@jwt_required()
def delete_attachment(attachment_id: int):
    user_id = get_current_user_id()
    attachment = (
        Attachment.query.join(Note)
        .filter(Attachment.id == attachment_id, Note.owner_id == user_id)
        .first()
    )
    if not attachment:
        return jsonify({"error": "Attachment not found"}), 404

    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], attachment.filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    db.session.delete(attachment)
    db.session.commit()
    return jsonify({"message": "Attachment deleted"})
