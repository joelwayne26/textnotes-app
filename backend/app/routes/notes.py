from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import or_, and_
from typing import Optional, List

from app.extensions import db
from app.models import Note, Tag, Folder

notes_bp = Blueprint("notes", __name__)


class NoteCreateSchema(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = ""
    folder_id: Optional[int] = None
    tag_ids: List[int] = []
    is_pinned: bool = False


class NoteUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    folder_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    is_pinned: Optional[bool] = None
    is_archived: Optional[bool] = None


def get_current_user_id() -> int:
    return int(get_jwt_identity())


@notes_bp.get("")
@jwt_required()
def list_notes():
    user_id = get_current_user_id()
    q = request.args.get("q", "").strip()
    folder_id = request.args.get("folder_id")
    tag_id = request.args.get("tag_id")
    archived = request.args.get("archived", "false").lower() == "true"
    pinned = request.args.get("pinned")

    query = Note.query.filter_by(owner_id=user_id, is_archived=archived)

    if folder_id:
        query = query.filter_by(folder_id=int(folder_id))
    if tag_id:
        query = query.filter(Note.tags.any(Tag.id == int(tag_id)))
    if pinned is not None:
        query = query.filter_by(is_pinned=pinned.lower() == "true")

    if q:
        # Simple full-text like search (title + content)
        search = f"%{q}%"
        query = query.filter(
            or_(Note.title.ilike(search), Note.content.ilike(search))
        )

    notes = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc()).all()
    return jsonify([n.to_dict(include_content=False) for n in notes])


@notes_bp.post("")
@jwt_required()
def create_note():
    user_id = get_current_user_id()
    try:
        data = NoteCreateSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400

    if data.folder_id:
        folder = Folder.query.filter_by(id=data.folder_id, owner_id=user_id).first()
        if not folder:
            return jsonify({"error": "Folder not found"}), 404

    note = Note(
        title=data.title,
        content=data.content,
        folder_id=data.folder_id,
        is_pinned=data.is_pinned,
        owner_id=user_id,
    )

    if data.tag_ids:
        tags = Tag.query.filter(Tag.id.in_(data.tag_ids), Tag.owner_id == user_id).all()
        note.tags = tags

    db.session.add(note)
    db.session.commit()
    return jsonify(note.to_dict()), 201


@notes_bp.get("/<int:note_id>")
@jwt_required()
def get_note(note_id: int):
    user_id = get_current_user_id()
    note = Note.query.filter_by(id=note_id, owner_id=user_id).first()
    if not note:
        return jsonify({"error": "Note not found"}), 404
    return jsonify(note.to_dict())


@notes_bp.put("/<int:note_id>")
@jwt_required()
def update_note(note_id: int):
    user_id = get_current_user_id()
    note = Note.query.filter_by(id=note_id, owner_id=user_id).first()
    if not note:
        return jsonify({"error": "Note not found"}), 404

    try:
        data = NoteUpdateSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400

    if data.title is not None:
        note.title = data.title
    if data.content is not None:
        note.content = data.content
    if data.is_pinned is not None:
        note.is_pinned = data.is_pinned
    if data.is_archived is not None:
        note.is_archived = data.is_archived
    if data.folder_id is not None:
        if data.folder_id == 0:
            note.folder_id = None
        else:
            folder = Folder.query.filter_by(id=data.folder_id, owner_id=user_id).first()
            if not folder:
                return jsonify({"error": "Folder not found"}), 404
            note.folder_id = data.folder_id

    if data.tag_ids is not None:
        tags = Tag.query.filter(Tag.id.in_(data.tag_ids), Tag.owner_id == user_id).all()
        note.tags = tags

    db.session.commit()
    return jsonify(note.to_dict())


@notes_bp.delete("/<int:note_id>")
@jwt_required()
def delete_note(note_id: int):
    user_id = get_current_user_id()
    note = Note.query.filter_by(id=note_id, owner_id=user_id).first()
    if not note:
        return jsonify({"error": "Note not found"}), 404

    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Note deleted"}), 200
