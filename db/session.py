from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os

from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.auth_utils import get_current_user_id

load_dotenv()

Base = declarative_base()

_engine = None
_SessionLocal = None


def _get_engine():
    global _engine, _SessionLocal
    user = os.getenv("DB_ADMIN_USER")
    password = os.getenv("DB_ADMIN_PASSWORD")
    host = os.getenv("DB_ADMIN_HOST")
    port = os.getenv("DB_ADMIN_PORT", "5432")
    dbname = os.getenv("DB_ADMIN_NAME")
    # Build a key to detect env var changes between test files
    key = (user, password, host, port, dbname)
    if _engine is None or getattr(_engine, "_eps_key", None) != key:
        url = (
            f"postgresql+psycopg2://{user}:{password}"
            f"@{host}:{port}/{dbname}?sslmode=require"
        )
        _engine = create_engine(url, poolclass=NullPool)
        _engine._eps_key = key
        _SessionLocal = None
    return _engine


def _get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_get_engine(),
        )
    return _SessionLocal


# Dependencia para los endpoints de FastAPI
def get_db():
    db: Session = _get_session_local()()
    try:
        yield db
        db.commit()       
    except Exception:
        db.rollback() 
        raise
    finally:
        db.close()
        
def get_db_audit(
    user_id: int = Depends(get_current_user_id)
):
    db: Session = _get_session_local()()

    try:
        db.execute(
            text("SET LOCAL my.app_user_id = :uid"),
            {"uid": str(user_id)}
        )
        yield db
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()