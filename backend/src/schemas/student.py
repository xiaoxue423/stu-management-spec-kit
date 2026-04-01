from __future__ import annotations

from datetime import datetime

from backend.src.compat import dataclass_with_slots
from backend.src.models.student import Gender, Student


@dataclass_with_slots
class CreateStudentRequest:
    name: str
    gender: Gender

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("name is required")
        if not isinstance(self.gender, Gender):
            raise ValueError("gender must be one of: male,female")


@dataclass_with_slots
class UpdateStudentRequest:
    name: str
    gender: Gender
    updated_at: datetime

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("name is required")
        if not isinstance(self.gender, Gender):
            raise ValueError("gender must be one of: male,female")


@dataclass_with_slots
class StudentResponse:
    id: int
    student_no: str
    name: str
    gender: str
    updated_at: str

    @classmethod
    def from_model(cls, student: Student) -> "StudentResponse":
        return cls(
            id=student.id,
            student_no=student.student_no,
            name=student.name,
            gender=student.gender.value,
            updated_at=student.updated_at.isoformat(),
        )
