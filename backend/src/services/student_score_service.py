from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from backend.src.compat import dataclass_with_slots
from backend.src.models.exam_score import ExamScore
from backend.src.models.student import Student
from backend.src.schemas.score import UpsertScoreRequest
from backend.src.schemas.student import CreateStudentRequest, UpdateStudentRequest


class ErrorCode:
    VALIDATION = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    UNKNOWN = "UNKNOWN_ERROR"


class DomainError(Exception):
    status_code: int = 500
    error_code: str = ErrorCode.UNKNOWN

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationError(DomainError):
    status_code = 400
    error_code = ErrorCode.VALIDATION


class NotFoundError(DomainError):
    status_code = 404
    error_code = ErrorCode.NOT_FOUND


class ConflictError(DomainError):
    status_code = 409
    error_code = ErrorCode.CONFLICT


@dataclass_with_slots
class EditFormResponse:
    student: Student
    scores: list[ExamScore]


class StudentScoreService:
    """MVP: 使用内存结构模拟持久层与事务边界。"""

    def __init__(self) -> None:
        self._student_auto_id = 1
        self._student_no_seq = 1
        self._score_auto_id = 1
        self._students_by_id: dict[int, Student] = {}
        self._student_no_to_id: dict[str, int] = {}
        self._scores_by_key: dict[tuple[int, int, str], ExamScore] = {}

    def _next_student_no(self) -> str:
        if self._student_no_seq > 9999:
            raise ConflictError("student_no range exhausted")
        student_no = f"{self._student_no_seq:04d}"
        self._student_no_seq += 1
        return student_no

    def create_student(self, req: CreateStudentRequest) -> Student:
        try:
            req.validate()
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        student_no = self._next_student_no()
        if student_no in self._student_no_to_id:
            raise ConflictError("student_no already exists")

        now = datetime.utcnow()
        student = Student(
            id=self._student_auto_id,
            student_no=student_no,
            name=req.name,
            gender=req.gender,
            created_at=now,
            updated_at=now,
        )
        self._students_by_id[student.id] = student
        self._student_no_to_id[student.student_no] = student.id
        self._student_auto_id += 1
        return student

    def update_student(self, student_id: int, req: UpdateStudentRequest) -> Student:
        try:
            req.validate()
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        student = self._students_by_id.get(student_id)
        if not student:
            raise NotFoundError("student not found")

        # 乐观并发：updated_at 不一致时拒绝覆盖
        if student.updated_at != req.updated_at:
            raise ConflictError("student version conflict")

        student.name = req.name
        student.gender = req.gender
        student.updated_at = datetime.utcnow()
        return student

    def upsert_score(self, student_id: int, req: UpsertScoreRequest) -> ExamScore:
        try:
            req.validate()
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        if student_id not in self._students_by_id:
            raise NotFoundError("student not found")

        key = (student_id, req.month, req.subject.value)
        now = datetime.utcnow()
        saved = self._scores_by_key.get(key)
        if saved:
            saved.score = Decimal(req.score)
            saved.updated_at = now
            return saved

        score = ExamScore(
            id=self._score_auto_id,
            student_id=student_id,
            month=req.month,
            subject=req.subject,
            score=Decimal(req.score),
            created_at=now,
            updated_at=now,
        )
        self._scores_by_key[key] = score
        self._score_auto_id += 1
        return score

    def get_edit_form(self, student_id: int) -> EditFormResponse:
        student = self._students_by_id.get(student_id)
        if not student:
            raise NotFoundError("student not found")
        scores = [s for s in self._scores_by_key.values() if s.student_id == student_id]
        scores.sort(key=lambda s: (s.month, s.subject.value))
        return EditFormResponse(student=student, scores=scores)

    def list_students(self) -> list[Student]:
        students = list(self._students_by_id.values())
        students.sort(key=lambda s: s.id)
        return students
