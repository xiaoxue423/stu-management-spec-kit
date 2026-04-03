"""Student and exam score workflows backed by MySQL via repositories."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src.compat import dataclass_with_slots
from backend.src.models.exam_score import ExamScore
from backend.src.models.student import Student
from backend.src.repositories.score_repository import ScoreRepository
from backend.src.repositories.student_repository import StudentRepository
from backend.src.schemas.score import UpsertScoreRequest
from backend.src.schemas.student import CreateStudentRequest, UpdateStudentRequest
from backend.src.services.errors import ConflictError, DomainError, NotFoundError, ValidationError


@dataclass_with_slots
class EditFormResponse:
    student: Student
    scores: list[ExamScore]


class StudentScoreService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._students = StudentRepository(session)
        self._scores = ScoreRepository(session)

    def create_student(self, req: CreateStudentRequest) -> Student:
        try:
            req.validate()
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        try:
            student_no = self._students.allocate_next_student_no()
            now = datetime.utcnow()
            student = self._students.insert_student(
                student_no=student_no,
                name=req.name.strip(),
                gender=req.gender,
                now=now,
            )
            self._session.commit()
            return student
        except DomainError:
            self._session.rollback()
            raise
        except SQLAlchemyError:
            self._session.rollback()
            raise

    def update_student(self, student_id: int, req: UpdateStudentRequest) -> Student:
        try:
            req.validate()
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        try:
            now = datetime.utcnow()
            student = self._students.update_if_version_matches(
                student_id,
                name=req.name.strip(),
                gender=req.gender,
                expected_updated_at=req.updated_at,
                now=now,
            )
            self._session.commit()
            return student
        except DomainError:
            self._session.rollback()
            raise
        except SQLAlchemyError:
            self._session.rollback()
            raise

    def upsert_score(self, student_id: int, req: UpsertScoreRequest) -> ExamScore:
        try:
            req.validate()
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        if self._students.get_by_id(student_id) is None:
            raise NotFoundError("student not found")

        try:
            now = datetime.utcnow()
            score = self._scores.upsert(
                student_id,
                req.month,
                req.subject,
                Decimal(req.score),
                now,
            )
            self._session.commit()
            return score
        except DomainError:
            self._session.rollback()
            raise
        except SQLAlchemyError:
            self._session.rollback()
            raise

    def get_edit_form(self, student_id: int) -> EditFormResponse:
        student = self._students.get_by_id(student_id)
        if not student:
            raise NotFoundError("student not found")
        scores = self._scores.list_for_student(student_id)
        return EditFormResponse(student=student, scores=scores)

    def list_students(self) -> list[Student]:
        return self._students.list_sorted_by_id()
