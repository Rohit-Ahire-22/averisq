from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


DATABASE_URL = settings.database_url


# 1. Create the database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# 2. Create a session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# 3. Provide a database session to FastAPI
def get_db():
    db = SessionLocal()

    try:
        yield db

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()