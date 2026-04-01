from __future__ import annotations

from datetime import datetime
from enum import Enum

from backend.src.compat import dataclass_with_slots


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


@dataclass_with_slots
class Student:
    id: int
    student_no: str
    name: str
    gender: Gender
    created_at: datetime
    updated_at: datetime
