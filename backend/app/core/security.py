from pwdlib import PasswordHash

from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from app.core.config import settings

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(user_id: UUID) -> str:
    now = datetime.now(timezone.utc)

    expire = now + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return token

def decode_access_token(token: str) -> UUID:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={
                "require": ["sub", "iat", "exp"]
            }
        )

        subject = payload["sub"]

        if not isinstance(subject, str):
            raise ValueError("Invalid subject")

        user_id = UUID(subject)

        return user_id

    except (jwt.InvalidTokenError, ValueError, TypeError, KeyError):
        raise ValueError("Invalid or expired access token")