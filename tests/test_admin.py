import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.main import app
from src.models.model import User, UserRole
from src.db.database import get_session
from src.controllers.middleware.auth import get_current_user

# Mock admin user for dependency override
def override_get_current_user_admin():
    return User(id=1, username="adminuser", role=UserRole.ADMIN)

# Mock non-admin user for dependency override
def override_get_current_user_nonadmin():
    return User(id=2, username="normaluser", role=UserRole.USER)

# Override session to use test DB or a mock
@pytest.fixture
def session_override():
    # Implement your test DB session here
    with Session() as session:
        yield session

app.dependency_overrides[get_session] = session_override

client = TestClient(app)

def test_create_admin_success(monkeypatch):
    # Override current user to admin
    app.dependency_overrides[get_current_user] = override_get_current_user_admin

    # Mock session.exec to return no existing user
    def mock_exec(*args, **kwargs):
        class Result:
            def first(self):
                return None
        return Result()

    monkeypatch.setattr(Session, "exec", mock_exec)

    response = client.post("/api/create-admin", json={
        "username": "newadmin",
        "email": "newadmin@example.com",
        "password": "strongpassword"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Admin account created successfully"
    assert data["user"] == "newadmin"




def test_create_admin_forbidden():
    # Override current user to non-admin
    app.dependency_overrides[get_current_user] = override_get_current_user_nonadmin

    response = client.post("/api/create-admin", json={
        "username": "newadmin",
        "email": "newadmin@example.com",
        "password": "strongpassword"
    })

    assert response.status_code == 403
    assert response.json()["detail"] == "Access forbidden: Admins only"

def test_create_admin_username_exists(monkeypatch):
    app.dependency_overrides[get_current_user] = override_get_current_user_admin

    # Mock session.exec to return an existing user
    def mock_exec(*args, **kwargs):
        class Result:
            def first(self):
                return User(username="existinguser")
        return Result()

    monkeypatch.setattr(Session, "exec", mock_exec)

    response = client.post("/api/create-admin", json={
        "username": "existinguser",
        "email": "existing@example.com",
        "password": "strongpassword"
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Username or email already exists"

