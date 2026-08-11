from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from app.config import Settings
from app.extensions import db
from app.routes import register_blueprints


def create_app(config: Settings | None = None) -> Flask:
    app = Flask(__name__)

    settings = config or Settings()
    app.config.from_mapping(settings.model_dump())

    # Extensions
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)
    CORS(
        app,
        origins=settings.CORS_ORIGINS,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
    )

    # Blueprints
    register_blueprints(app)

    # Health check
    @app.get("/health")
    def health():
        return {"status": "ok", "service": "notes-api"}

    return app
