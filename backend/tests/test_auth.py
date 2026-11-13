def test_register_user(client, db_session):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "StrongPassword123"
        }
    )

    assert response.status_code == 201

    from sqlalchemy import select
    from app.models.user import User

    user = db_session.scalar(
        select(User).where(
            User.email == "newuser@example.com"
        )
    )

    assert user is not None
    assert user.email == "newuser@example.com"
    assert user.password_hash != "StrongPassword123"

def test_register_duplicate_email(client):
    user_data = {
        "email": "duplicate@example.com",
        "password": "StrongPassword123"
    }

    first_response = client.post(
        "/api/v1/auth/register",
        json=user_data
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/auth/register",
        json=user_data
    )

    assert second_response.status_code == 409

def test_login_user(client):
    # Register a user first
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "loginuser@example.com",
            "password": "StrongPassword123"
        }
    )

    assert register_response.status_code == 201

    # Login with the same credentials
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "StrongPassword123"
        }
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_with_wrong_password(client):
    # Register a user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "StrongPassword123"
        }
    )

    # Attempt login with an incorrect password
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "WrongPassword456"
        }
    )

    assert response.status_code == 401

def test_login_with_nonexistent_email(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "StrongPassword123"
        }
    )

    assert response.status_code == 401

def test_login_token_can_access_protected_endpoint(client):
    # Register a user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "tokenuser@example.com",
            "password": "StrongPassword123"
        }
    )

    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "tokenuser@example.com",
            "password": "StrongPassword123"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Access a protected endpoint using the token
    response = client.get(
        "/api/v1/monitors/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200