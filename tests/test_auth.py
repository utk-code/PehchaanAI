from fastapi.testclient import TestClient

# Fixtures (client, auth_token, auth_headers, db_session) are provided by
# tests/conftest.py, which sets DATABASE_URL/JWT_SECRET_KEY before app import.


def test_register_user_returns_access_token(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "investigator@example.org",
            "password": "StrongPass123!",
            "full_name": "Case Investigator",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    user_payload = {
        "email": "duplicate@example.org",
        "password": "StrongPass123!",
        "full_name": "Duplicate User",
    }

    first_response = client.post("/auth/register", json=user_payload)
    second_response = client.post("/auth/register", json=user_payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already registered"


def test_login_returns_access_token_for_valid_credentials(client: TestClient) -> None:
    user_payload = {
        "email": "login@example.org",
        "password": "StrongPass123!",
        "full_name": "Login User",
    }
    client.post("/auth/register", json=user_payload)

    response = client.post(
        "/auth/login",
        data={
            "username": user_payload["email"],
            "password": user_payload["password"],
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_rejects_invalid_credentials(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        data={
            "username": "missing@example.org",
            "password": "WrongPass123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_me_requires_valid_bearer_token(client: TestClient) -> None:
    user_payload = {
        "email": "me@example.org",
        "password": "StrongPass123!",
        "full_name": "Current User",
    }
    register_response = client.post("/auth/register", json=user_payload)
    token = register_response.json()["access_token"]

    unauthorized_response = client.get("/auth/me")
    authorized_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert unauthorized_response.status_code == 401
    assert authorized_response.status_code == 200
    assert authorized_response.json()["email"] == user_payload["email"]
    assert authorized_response.json()["full_name"] == user_payload["full_name"]


# --------------------------------------------------------------------------- #
# Authentication security edge cases (100% coverage target)
# --------------------------------------------------------------------------- #
def test_me_rejects_garbage_bearer_token(client: TestClient) -> None:
    """A malformed JWT is rejected with 401."""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-jwt-at-all"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_me_rejects_token_without_subject(client: TestClient) -> None:
    """A validly-signed token without a subject is rejected with 401."""
    from datetime import datetime, timedelta, timezone

    from jose import jwt

    from backend.config import get_settings

    settings = get_settings()
    token = jwt.encode(
        {"exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_me_rejects_token_for_unknown_user(client: TestClient) -> None:
    """A valid token for a user that no longer exists is rejected with 401."""
    from backend.auth.security import create_access_token

    token = create_access_token("00000000-0000-0000-0000-000000000000")
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_me_rejects_inactive_user(client: TestClient, db_session) -> None:
    """Inactive users cannot authenticate even with a valid token."""
    from backend.auth.security import create_access_token
    from backend.database.models import User

    user = User(
        email="inactive@example.org",
        full_name="Inactive User",
        hashed_password="unusable",
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()

    token = create_access_token(user.id)
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_login_existing_user_wrong_password_returns_401(client: TestClient) -> None:
    """Wrong password for an existing account is rejected (not just unknown email)."""
    user_payload = {
        "email": "wrongpw@example.org",
        "password": "StrongPass123!",
        "full_name": "Wrong Password User",
    }
    client.post("/auth/register", json=user_payload)

    response = client.post(
        "/auth/login",
        data={
            "username": user_payload["email"],
            "password": "TotallyWrong123!",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_duplicate_email_race_returns_409(client: TestClient, db_session) -> None:
    """A registration race that hits the unique constraint returns 409."""
    from unittest.mock import patch

    from sqlalchemy import select

    from backend.auth import routes as auth_routes
    from backend.database.models import User

    # Email exists in the DB, but the pre-check is made to miss it
    db_session.add(
        User(
            email="race@example.org",
            full_name="Existing User",
            hashed_password="pre-existing",
        )
    )
    db_session.commit()

    payload = {
        "email": "race@example.org",
        "password": "StrongPass123!",
        "full_name": "Racing User",
    }
    with patch.object(auth_routes, "select", return_value=select(User).where(False)):
        response = client.post("/auth/register", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


def test_health_endpoint_returns_ok(client: TestClient) -> None:
    """The health probe reports the API is up."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
