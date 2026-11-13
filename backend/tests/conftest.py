import pytest

from app.db.base import Base

from sqlalchemy.orm import Session

from tests.test_database import TestSessionLocal, test_engine

from fastapi.testclient import TestClient

from uuid import uuid4

from app.core.security import create_access_token
from app.models.user import User

from app.main import app
from app.db.database import get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()

    session = TestSessionLocal(
        bind=connection,
        join_transaction_mode="create_savepoint"
    )

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture
def authenticated_client(client, db_session):
    test_user = User(
        id=uuid4(),
        email="auth_test@example.com",
        password_hash="test_hash"
    )

    db_session.add(test_user)
    db_session.flush()

    token = create_access_token(test_user.id)

    client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    return client