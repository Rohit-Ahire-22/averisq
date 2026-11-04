import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
import app.models
from uuid import uuid4,UUID
from app.models.user import User

BACKEND_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BACKEND_DIR / ".env")

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)

def test_database_session_rollback(db_session):
    from app.models.monitor import Monitor

    test_user = User(
        id=UUID("550e8400-e29b-41d4-a716-446655440000"),
        email="test@example.com",
        password_hash="test_hash"
    )

    db_session.add(test_user)
    db_session.flush()

    monitor = Monitor(
        id=uuid4(),
        user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
        name="Rollback Test",
        url="https://example.com",
        interval=60,
        status="active"
    )

    db_session.add(monitor)
    db_session.commit()

    saved_monitor = db_session.get(Monitor, monitor.id)

    assert saved_monitor is not None
    assert saved_monitor.name == "Rollback Test"

def test_monitor_does_not_persist(db_session):
    from sqlalchemy import select
    from app.models.monitor import Monitor

    statement = select(Monitor).where(
        Monitor.name == "Rollback Test"
    )

    monitor = db_session.scalar(statement)

    assert monitor is None

def test_monitor_lifecycle(client, db_session):
    # Arrange: create a user
    test_user = User(
        id=UUID("550e8400-e29b-41d4-a716-446655440000"),
        email="test@example.com",
        password_hash="test_hash"
    )

    db_session.add(test_user)
    db_session.flush()

    # Create a monitor through the API
    create_response = client.post(
        "/api/v1/monitors/",
        json={
            "name": "Lifecycle Monitor",
            "url": "https://example.com",
            "interval": 60
        }
    )

    assert create_response.status_code == 201

    monitor_id = create_response.json()["id"]

    # 1. Retrieve the monitor
    get_response = client.get(
        f"/api/v1/monitors/{monitor_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Lifecycle Monitor"

    # 2. Update the monitor
    update_response = client.patch(
        f"/api/v1/monitors/{monitor_id}",
        json={"name": "Updated Monitor"}
    )

    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Monitor"

    # 3. Delete the monitor
    delete_response = client.delete(
        f"/api/v1/monitors/{monitor_id}"
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    # 4. Confirm it no longer exists
    missing_response = client.get(
        f"/api/v1/monitors/{monitor_id}"
    )

    assert missing_response.status_code == 404

def test_monitor_not_found(client):
    missing_id = UUID("00000000-0000-0000-0000-000000000001")

    # GET
    get_response = client.get(
        f"/api/v1/monitors/{missing_id}"
    )
    assert get_response.status_code == 404

    # PATCH
    update_response = client.patch(
        f"/api/v1/monitors/{missing_id}",
        json={"name": "Updated"}
    )
    assert update_response.status_code == 404

    # DELETE
    delete_response = client.delete(
        f"/api/v1/monitors/{missing_id}"
    )
    assert delete_response.status_code == 404