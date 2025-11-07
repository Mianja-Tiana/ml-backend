import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.main import app
from src.db.database import get_session
from src.models.model import UserRole, User
from unittest.mock import MagicMock
from src.controllers.middleware.auth import get_current_user

client = TestClient(app)

admin_user = User(
    id=1,
    username="admin",
    roles=[MagicMock(role=MagicMock(name="admin"))],
    role=UserRole.ADMIN
)
normal_user = User(
    id=2,
    username="user",
    roles=[MagicMock(role=MagicMock(name="user"))],
    role=UserRole.USER
)

@pytest.fixture
def override_get_current_user_admin():
    def _override():
        return admin_user
    app.dependency_overrides[get_current_user] = _override
    yield
    app.dependency_overrides.pop(get_current_user)

@pytest.fixture
def override_get_current_user_normal():
    def _override():
        return normal_user
    app.dependency_overrides[get_current_user] = _override
    yield
    app.dependency_overrides.pop(get_current_user)

@pytest.fixture
def override_get_session():
    def _override():
        session = MagicMock(spec=Session)
        session.exec.return_value.all.return_value = []
        yield session
    app.dependency_overrides[get_session] = _override
    yield
    app.dependency_overrides.pop(get_session)


# Telecom Churn API - User tests

def test_telecomchurn_get_me_returns_current_user(override_get_current_user_admin):
    response = client.get("/api/users/me")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == admin_user.username

def test_telecomchurn_list_users_admin_allowed(override_get_current_user_admin, override_get_session):
    session = MagicMock(spec=Session)
    session.exec.return_value.all.return_value = [admin_user, normal_user]
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    response = client.get("/api/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_telecomchurn_list_users_non_admin_forbidden(override_get_current_user_normal):
    response = client.get("/api/users/")
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


# Telecom Churn API - Feedback tests

def test_telecomchurn_create_feedback_success(override_get_current_user_normal, override_get_session):
    feedback_payload = {
        "prediction_id": 1,
        "correct": True,
        "comment": "Good prediction"
    }
    response = client.post("/api/feedback/", json=feedback_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction_id"] == 1
    assert data["correct"] is True

def test_telecomchurn_list_feedback_admin_allowed(override_get_current_user_admin, override_get_session):
    response = client.get("/api/feedback/")
    assert response.status_code == 200

def test_telecomchurn_list_feedback_non_admin_forbidden(override_get_current_user_normal):
    response = client.get("/api/feedback/")
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"



# Telecom Churn API - MLModel tests

def test_telecomchurn_list_models_admin_allowed(override_get_current_user_admin, override_get_session):
    response = client.get("/api/models/")
    assert response.status_code == 200

def test_telecomchurn_list_models_non_admin_forbidden(override_get_current_user_normal):
    response = client.get("/api/models/")
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"

@pytest.mark.skip(reason="Requires MLflow mocking")
def test_telecomchurn_create_model_success(override_get_current_user_admin, override_get_session):
    model_payload = {
        "name": "TestModel",
        "description": "Test description"
    }
    response = client.post("/api/models/", json=model_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestModel"

def test_telecomchurn_create_model_non_admin_forbidden(override_get_current_user_normal):
    model_payload = {
        "name": "TestModel",
        "description": "Test description"
    }
    response = client.post("/api/models/", json=model_payload)
    assert response.status_code == 403


# Telecom Churn API - Prediction Log tests
def test_telecomchurn_list_logs_admin_allowed(override_get_current_user_admin, override_get_session):
    response = client.get("/api/logs/")
    assert response.status_code == 200

def test_telecomchurn_list_logs_non_admin_forbidden(override_get_current_user_normal):
    response = client.get("/api/logs/")
    assert response.status_code == 403
    assert response.json()["detail"] == "Access forbidden: Admins only"
