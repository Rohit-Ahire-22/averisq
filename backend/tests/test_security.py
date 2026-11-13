
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


# -------------------------
# Test helpers
# -------------------------

def create_test_token(payload: dict, secret: str | None = None) -> str:
    signing_key = secret or settings.jwt_secret_key

    return jwt.encode(
        payload,
        signing_key,
        algorithm=settings.jwt_algorithm,
    )


# -------------------------
# Password security tests
# -------------------------

def test_password_is_hashed():
    password = "StrongPassword123"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password)


def test_same_password_produces_different_hashes():
    password = "StrongPassword123"

    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2


def test_wrong_password_is_rejected():
    hashed_password = hash_password("StrongPassword123")

    assert not verify_password("WrongPassword123", hashed_password)


# -------------------------
# JWT security tests
# -------------------------

def test_create_and_decode_access_token():
    user_id = uuid4()

    token = create_access_token(user_id)

    decoded_user_id = decode_access_token(token)

    assert decoded_user_id == user_id


def test_invalid_signature_is_rejected():
    user_id = uuid4()

    payload = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    # A separate, sufficiently long key intentionally creates
    # a token that our application must reject.
    wrong_secret = "wrong-secret-for-testing-only-123456789"

    token = create_test_token(payload, secret=wrong_secret)

    with pytest.raises(ValueError):
        decode_access_token(token)


def test_expired_token_is_rejected():
    user_id = uuid4()

    payload = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc) - timedelta(minutes=10),
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
    }

    token = create_test_token(payload)

    with pytest.raises(ValueError):
        decode_access_token(token)


def test_token_without_expiration_is_rejected():
    user_id = uuid4()

    payload = {
        "sub": str(user_id),
        "iat": datetime.now(timezone.utc),
    }

    token = create_test_token(payload)

    with pytest.raises(ValueError):
        decode_access_token(token)


def test_invalid_user_id_in_subject_is_rejected():
    payload = {
        "sub": "not-a-valid-uuid",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    token = create_test_token(payload)

    with pytest.raises(ValueError):
        decode_access_token(token)
