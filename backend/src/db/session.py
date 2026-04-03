"""Engine and session factory. DATABASE_URL read on first use (mysql+pymysql://...)."""

from __future__ import annotations

import os
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

_engine: Engine | None = None
_session_factory: sessionmaker[Any] | None = None


def _ensure_engine() -> None:
    global _engine, _session_factory
    if _engine is not None:
        return
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Example: "
            "mysql+pymysql://user:pass@127.0.0.1:3306/dbname?charset=utf8mb4"
        )
    _engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
    )
    _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def get_engine() -> Engine:
    _ensure_engine()
    assert _engine is not None
    return _engine


class _SessionLocalFactory:
    def __call__(self) -> Session:
        _ensure_engine()
        assert _session_factory is not None
        return _session_factory()


SessionLocal = _SessionLocalFactory()


def dispose_engine() -> None:
    """Release pool on app shutdown (safe if engine was never created)."""
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
        _engine = None
        _session_factory = None
