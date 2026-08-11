from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from pydantic import BaseModel, EmailStr, Field, ValidationError

from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


class RegisterSchema(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=128)


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


@auth_bp.post("/register")
def register():
    try:
        data = RegisterSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400

    if User.query.filter((User.email == data.email) | (User.username == data.username)).first():
        return jsonify({"error": "Email or username already exists"}), 409

    user = User(email=data.email, username=data.username)
    user.set_password(data.password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "User created successfully",
        "user": user.to_dict(),
        "access_token": access_token,
    }), 201


@auth_bp.post("/login")
def login():
    try:
        data = LoginSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.errors()}), 400

    user = User.query.filter_by(email=data.email).first()
    if not user or not user.check_password(data.password):
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is disabled"}), 403

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "Login successful",
        "user": user.to_dict(),
        "access_token": access_token,
    })


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())
