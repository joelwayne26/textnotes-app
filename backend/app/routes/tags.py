from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import BaseModel, Field, ValidationError
from typing import Optional

from app.extensions import db
from app.models import Tag

tags_bp = Blueprint("tags", __name__)


class TagSchema(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


def get_current_user_id() -> int:
    return int(get_jwt_identity())


@tags_bp.get("")
@jwt_required()
def list_tags():
    user_id = get_current_user_id()
    tags = Tag.query.filter_by(owner_id=user_id).order_by(Tag.name).all()
    return jsonify([t.to_dict() for t in tags])


@tags_bp.post("")
@jwt_required()
def create_tag():
    user_id = get_current_user_id()
    try:
        data = TagSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400

    existing = Tag.query.filter_by(name=data.name, owner_id=user_id).first()
    if existing:
        return jsonify({"error": "Tag already exists"}), 409

    tag = Tag(name=data.name, color=data.color or "#6366f1", owner_id=user_id)
    db.session.add(tag)
    db.session.commit()
    return jsonify(tag.to_dict()), 201


@tags_bp.delete("/<int:tag_id>")
@jwt_required()
def delete_tag(tag_id: int):
    user_id = get_current_user_id()
    tag = Tag.query.filter_by(id=tag_id, owner_id=user_id).first()
    if not tag:
        return jsonify({"error": "Tag not found"}), 404

    db.session.delete(tag)
    db.session.commit()
    return jsonify({"message": "Tag deleted"})
