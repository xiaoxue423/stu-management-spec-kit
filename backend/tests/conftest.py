"""Shared fixtures for backend tests. Contract tests require MySQL and DATABASE_URL."""

from __future__ import annotations

import os

import pytest
from sqlalchemy import text


def pytest_collection_modifyitems(config, items) -> None:
    if os.environ.get("DATABASE_URL"):
        return
    skip_db = pytest.mark.skip(
        reason="DATABASE_URL must point at MySQL for contract tests (see backend/docs/mysql-setup.md)"
    )
    for item in items:
        if "/contract/" in str(item.path).replace("\\", "/"):
            item.add_marker(skip_db)


@pytest.fixture(autouse=True)
def _reset_mysql_tables_for_contract_tests(request):
    """Keep contract tests isolated when running against a dev MySQL."""
    if not os.environ.get("DATABASE_URL"):
        yield
        return
    if "contract" not in str(request.path):
        yield
        return

    from backend.src.db.session import SessionLocal

    db = SessionLocal()
    try:
        db.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        db.execute(text("TRUNCATE TABLE exam_scores"))
        db.execute(text("TRUNCATE TABLE students"))
        db.execute(text("UPDATE student_no_seq SET next_val = 0 WHERE id = 1"))
        db.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        db.commit()
    finally:
        db.close()
    yield
