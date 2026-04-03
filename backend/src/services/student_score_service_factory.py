"""Construct StudentScoreService with the current request session."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.src.services.student_score_service import StudentScoreService


def get_student_score_service(session: Session) -> StudentScoreService:
    return StudentScoreService(session)
