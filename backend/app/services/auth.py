
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate,UserLogin


def register_user(db: Session, user_data: UserCreate) -> User:
    email = user_data.email.strip().lower()

    # 1. Check whether the email is already registered
    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user is not None:
        raise ValueError("Email already registered")

    # 2. Create the user object
    user = User(
        id=uuid4(),
        email=email,
        password_hash=hash_password(user_data.password),
    )

    # 3. Save the user to the database
    db.add(user)

    try:
        db.commit()
        db.refresh(user)

    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Email already registered") from exc

    return user

def authenticate_user(db: Session, user_data: UserLogin) -> User:
    email = user_data.email.strip().lower()

    # 1. Find user by email
    user = db.scalar(
        select(User).where(User.email == email)
    )

    # 2. Check whether user exists
    if user is None:
        raise ValueError("Invalid email or password")

    # 3. Verify submitted password against stored hash
    if not verify_password(
        user_data.password,
        user.password_hash
    ):
        raise ValueError("Invalid email or password")

    return user
