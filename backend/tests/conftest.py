"""
Pytest configuration and fixtures for Notes API tests
"""

import pytest
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def app():
    """Create application for testing"""
    from app import create_app
    
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test-secret-key"
    
    with app.app_context():
        from app.extensions import db
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Create authenticated headers"""
    # First register a user
    client.post("/api/auth/register", json={
        "email": "auth@test.com",
        username="authuser",
        password: "testpass123"
    })
    
    # Then login
    response = client.post("/api/auth/login", json={
        "email": "auth@test.com",
        password: "testpass123"
    })
    
    token = response.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}
