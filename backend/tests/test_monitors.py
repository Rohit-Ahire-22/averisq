from uuid import UUID, uuid4

from app.core.security import create_access_token
from app.models.user import User


def test_create_monitor(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/monitors/",
        json={
            "name": "Test Monitor",
            "url": "https://example.com",
            "interval": 60
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Monitor"
    assert data["url"] == "https://example.com/"
    assert data["interval"] == 60
    assert data["status"] == "active"

def test_create_monitor_rejects_invalid_interval(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/monitors/",
        json={
            "name": "Invalid Monitor",
            "url": "https://example.com",
            "interval": 5
        }
    )

    assert response.status_code == 422

def test_get_monitors(authenticated_client):
    response = authenticated_client.get("/api/v1/monitors/")

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert "total" in data
    assert data["total"] == 0
    assert data["items"] == []

def test_user_cannot_access_another_users_monitor(client, db_session):
    # Create two users
    user_a = User(
        id=uuid4(),
        email="user_a@example.com",
        password_hash="test_hash"
    )

    user_b = User(
        id=uuid4(),
        email="user_b@example.com",
        password_hash="test_hash"
    )

    db_session.add_all([user_a, user_b])
    db_session.flush()

    # Generate separate access tokens
    token_a = create_access_token(user_a.id)
    token_b = create_access_token(user_b.id)

    # Authenticate as User A
    client.headers.update({
        "Authorization": f"Bearer {token_a}"
    })

    # User A creates a monitor
    create_response = client.post(
        "/api/v1/monitors/",
        json={
            "name": "Private Monitor",
            "url": "https://example.com",
            "interval": 60
        }
    )

    assert create_response.status_code == 201

    monitor_id = create_response.json()["id"]

    # Switch authentication to User B
    client.headers.update({
        "Authorization": f"Bearer {token_b}"
    })

    # User B should not see User A's monitor in their list
    list_response = client.get("/api/v1/monitors/")

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 0

    # User B tries to update User A's monitor
    update_response = client.patch(
        f"/api/v1/monitors/{monitor_id}",
        json={"name": "Hacked Monitor"}
    )

    assert update_response.status_code == 404

    # User B tries to delete User A's monitor
    delete_response = client.delete(
        f"/api/v1/monitors/{monitor_id}"
    )

    assert delete_response.status_code == 404

    # User B tries to access User A's monitor
    get_response = client.get(
        f"/api/v1/monitors/{monitor_id}"
    )

    assert get_response.status_code == 404

def test_monitor_endpoints_require_authentication(client):
    response = client.get("/api/v1/monitors/")

    assert response.status_code == 401