from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import BaseModel, Field, ValidationError
from typing import Optional

from app.extensions import db
from app.models import Folder

folders_bp = Blueprint("folders", __name__)


class FolderSchema(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    parent_id: Optional[int] = None


def get_current_user_id() -> int:
    return int(get_jwt_identity())


@folders_bp.get("")
@jwt_required()
def list_folders():
    user_id = get_current_user_id()
    folders = Folder.query.filter_by(owner_id=user_id, parent_id=None).order_by(Folder.name).all()
    return jsonify([f.to_dict(include_children=True) for f in folders])


@folders_bp.post("")
@jwt_required()
def create_folder():
    user_id = get_current_user_id()
    try:
        data = FolderSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400

    if data.parent_id:
        parent = Folder.query.filter_by(id=data.parent_id, owner_id=user_id).first()
        if not parent:
            return jsonify({"error": "Parent folder not found"}), 404

    folder = Folder(name=data.name, parent_id=data.parent_id, owner_id=user_id)
    db.session.add(folder)
    db.session.commit()
    return jsonify(folder.to_dict()), 201


@folders_bp.put("/<int:folder_id>")
@jwt_required()
def update_folder(folder_id: int):
    user_id = get_current_user_id()
    folder = Folder.query.filter_by(id=folder_id, owner_id=user_id).first()
    if not folder:
        return jsonify({"error": "Folder not found"}), 404

    try:
        data = FolderSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400

    folder.name = data.name
    if data.parent_id is not None:
        if data.parent_id == 0:
            folder.parent_id = None
        else:
            parent = Folder.query.filter_by(id=data.parent_id, owner_id=user_id).first()
            if not parent or parent.id == folder.id:
                return jsonify({"error": "Invalid parent"}), 400
            folder.parent_id = data.parent_id

    db.session.commit()
    return jsonify(folder.to_dict())


@folders_bp.delete("/<int:folder_id>")
@jwt_required()
def delete_folder(folder_id: int):
    user_id = get_current_user_id()
    folder = Folder.query.filter_by(id=folder_id, owner_id=user_id).first()
    if not folder:
        return jsonify({"error": "Folder not found"}), 404

    db.session.delete(folder)
    db.session.commit()
    return jsonify({"message": "Folder deleted"})
