from decimal import Decimal

import pytest

from backend.src.models.exam_score import Subject
from backend.src.models.student import Gender
from backend.src.schemas.score import UpsertScoreRequest
from backend.src.schemas.student import CreateStudentRequest


def test_invalid_gender_rejected() -> None:
    req = CreateStudentRequest(student_no="S001", name="张三", gender="unknown")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        req.validate()


def test_invalid_month_rejected() -> None:
    req = UpsertScoreRequest(month=13, subject=Subject.MATH, score=Decimal("90"))
    with pytest.raises(ValueError):
        req.validate()


def test_invalid_subject_rejected() -> None:
    req = UpsertScoreRequest(month=6, subject="physics", score=Decimal("90"))  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        req.validate()


def test_valid_enum_values_pass() -> None:
    req = CreateStudentRequest(student_no="S001", name="张三", gender=Gender.MALE)
    req.validate()
