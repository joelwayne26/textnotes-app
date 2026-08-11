"""
Tests for Notes API
Run with: pytest backend/tests/ -v
"""

import pytest
import json
from datetime import datetime, timezone


class TestNoteModel:
    """Test Note model functionality"""
    
    def test_note_creation(self, app, test_user):
        """Test creating a new note"""
        from app.models import Note
        
        note = Note(
            title="Test Note",
            content="# Hello World\nThis is **markdown** content.",
            owner_id=test_user.id,
        )
        
        assert note.title == "Test Note"
        assert note.is_pinned is False
        assert note.is_archived is False
        assert note.owner_id == test_user.id
    
    def test_note_to_dict(self, app, test_user, test_note):
        """Test note serialization"""
        data = test_note.to_dict()
        
        assert "id" in data
        assert "title" in data
        assert "content" in data
        assert "tags" in data
        assert "created_at" in data
        assert data["title"] == "Test Note"
    
    def test_note_without_content(self, app, test_user):
        """Test note dict without content"""
        from app.models import Note
        
        note = Note(
            title="No Content",
            owner_id=test_user.id,
        )
        data = note.to_dict(include_content=False)
        
        assert "content" not in data


class TestAuthRoutes:
    """Test authentication endpoints"""
    
    def test_register_success(self, client):
        """Test user registration"""
        response = client.post("/api/auth/register", json={
            "email": "newuser@test.com",
            "username": "newuser",
            "password": "securepassword123",
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert "token" in data
        assert data["user"]["email"] == "newuser@test.com"
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email"""
        response = client.post("/api/auth/register", json={
            "email": test_user.email,
            "username": "different",
            "password": "password123",
        })
        
        assert response.status_code == 400
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "testpassword",
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert "token" in data
    
    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "wrongpassword",
        })
        
        assert response.status_code == 401


class TestNoteRoutes:
    """Test note CRUD endpoints"""
    
    def test_create_note(self, client, auth_token):
        """Test creating a new note"""
        response = client.post("/api/notes", 
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "title": "New Note via API",
                "content": "Content here",
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["title"] == "New Note via API"
    
    def test_get_notes(self, client, auth_token, test_note):
        """Test retrieving notes list"""
        response = client.get(
            "/api/notes",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1
    
    def test_get_single_note(self, client, auth_token, test_note):
        """Test retrieving single note"""
        response = client.get(
            f"/api/notes/{test_note.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == test_note.id
    
    def test_update_note(self, client, auth_token, test_note):
        """Test updating a note"""
        response = client.put(
            f"/api/notes/{test_note.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "title": "Updated Title",
                "content": "Updated content",
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["title"] == "Updated Title"
    
    def test_delete_note(self, client, auth_token, test_note):
        """Test deleting a note"""
        response = client.delete(
            f"/api/notes/{test_note.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(
            f"/api/notes/{test_note.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert get_response.status_code == 404


class TestFolderAndTagRoutes:
    """Test folder and tag endpoints"""
    
    def test_create_folder(self, client, auth_token):
        """Test creating a folder"""
        response = client.post("/api/folders",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"name": "Work Projects"}
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Work Projects"
    
    def test_create_tag(self, client, auth_token):
        """Test creating a tag"""
        response = client.post("/api/tags",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "important",
                "color": "#ef4444",
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "important"


# Fixtures would be defined in conftest.py
@pytest.fixture
def app():
    """Create application fixture"""
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def db_session(app):
    """Create database session"""
    with app.app_context():
        from app.extensions import db
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_user(db_session):
    """Create test user"""
    from app.models import User
    user = User(
        email="test@example.com",
        username="testuser",
    )
    user.set_password("testpassword")
    db_session.session.add(user)
    db_session.session.commit()
    return user

@pytest.fixture
def test_note(db_session, test_user):
    """Create test note"""
    from app.models import Note
    note = Note(
        title="Test Note",
        content="Test content with **markdown**",
        owner_id=test_user.id,
    )
    db_session.session.add(note)
    db_session.session.commit()
    return note

@pytest.fixture
def auth_token(client, test_user):
    """Get auth token for test user"""
    response = client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "testpassword",
    })
    return response.get_json()["token"]
