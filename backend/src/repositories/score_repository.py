"""Exam score upsert and list by student."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.src.models.exam_score import ExamScore, Subject
from backend.src.models.orm.tables import ExamScoreRow


class ScoreRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert(
        self,
        student_id: int,
        month: int,
        subject: Subject,
        score: Decimal,
        now: datetime,
    ) -> ExamScore:
        subject_val = subject.value
        existing = (
            self._session.execute(
                select(ExamScoreRow).where(
                    ExamScoreRow.student_id == student_id,
                    ExamScoreRow.month == month,
                    ExamScoreRow.subject == subject_val,
                )
            )
            .scalars()
            .one_or_none()
        )
        if existing:
            existing.score = score
            existing.updated_at = now
            self._session.flush()
            return self._to_domain(existing)

        row = ExamScoreRow(
            student_id=student_id,
            month=month,
            subject=subject_val,
            score=score,
            created_at=now,
            updated_at=now,
        )
        self._session.add(row)
        self._session.flush()
        return self._to_domain(row)

    def list_for_student(self, student_id: int) -> list[ExamScore]:
        rows = (
            self._session.execute(select(ExamScoreRow).where(ExamScoreRow.student_id == student_id))
            .scalars()
            .all()
        )
        rows = sorted(rows, key=lambda r: (r.month, r.subject))
        return [self._to_domain(r) for r in rows]

    @staticmethod
    def _to_domain(row: ExamScoreRow) -> ExamScore:
        return ExamScore(
            id=row.id,
            student_id=row.student_id,
            month=row.month,
            subject=Subject(row.subject),
            score=Decimal(row.score),
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
