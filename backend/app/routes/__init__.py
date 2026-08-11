from flask import Flask

from app.routes.auth import auth_bp
from app.routes.notes import notes_bp
from app.routes.folders import folders_bp
from app.routes.tags import tags_bp
from app.routes.attachments import attachments_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(notes_bp, url_prefix="/api/notes")
    app.register_blueprint(folders_bp, url_prefix="/api/folders")
    app.register_blueprint(tags_bp, url_prefix="/api/tags")
    app.register_blueprint(attachments_bp, url_prefix="/api/attachments")
