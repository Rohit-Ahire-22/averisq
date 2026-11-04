from uuid import UUID

from app.models.user import User


def test_create_monitor(client, db_session):
    # Arrange: create a user for the monitor
    test_user = User(
        id=UUID("550e8400-e29b-41d4-a716-446655440000"),
        email="test@example.com",
        password_hash="test_hash"
    )

    db_session.add(test_user)
    db_session.flush()

    # Act: send an HTTP request
    response = client.post(
        "/api/v1/monitors/",
        json={
            "name": "Test Monitor",
            "url": "https://example.com",
            "interval": 60
        }
    )

    # Assert: verify the response
    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Monitor"
    assert data["url"] == "https://example.com/"
    assert data["interval"] == 60
    assert data["status"] == "active"

def test_create_monitor_rejects_invalid_interval(client):
    response = client.post(
        "/api/v1/monitors/",
        json={
            "name": "Invalid Monitor",
            "url": "https://example.com",
            "interval": 5
        }
    )

    assert response.status_code == 422

def test_get_monitors(client, db_session):
    test_user = User(
        id=UUID("550e8400-e29b-41d4-a716-446655440000"),
        email="test@example.com",
        password_hash="test_hash"
    )

    db_session.add(test_user)
    db_session.flush()

    response = client.get("/api/v1/monitors/")

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert "total" in data
    assert data["total"] == 0
    assert data["items"] == []