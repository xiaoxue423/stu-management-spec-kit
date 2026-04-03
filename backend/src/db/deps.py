"""FastAPI dependencies for database session."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from backend.src.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
