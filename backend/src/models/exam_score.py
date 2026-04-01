from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from backend.src.compat import dataclass_with_slots


class Subject(str, Enum):
    MATH = "math"
    CHINESE = "chinese"
    ENGLISH = "english"


@dataclass_with_slots
class ExamScore:
    id: int
    student_id: int
    month: int
    subject: Subject
    score: Decimal
    created_at: datetime
    updated_at: datetime
