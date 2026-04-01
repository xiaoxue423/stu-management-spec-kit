from __future__ import annotations

from decimal import Decimal

from backend.src.compat import dataclass_with_slots
from backend.src.models.exam_score import ExamScore, Subject


@dataclass_with_slots
class UpsertScoreRequest:
    month: int
    subject: Subject
    score: Decimal

    def validate(self) -> None:
        if self.month < 1 or self.month > 12:
            raise ValueError("month must be between 1 and 12")
        if self.score < Decimal("0") or self.score > Decimal("100"):
            raise ValueError("score must be between 0 and 100")
        if self.score.quantize(Decimal("0.01")) != self.score:
            raise ValueError("score supports at most 2 decimal places")


@dataclass_with_slots
class ScoreResponse:
    id: int
    student_id: int
    month: int
    subject: str
    score: str
    updated_at: str

    @classmethod
    def from_model(cls, score: ExamScore) -> "ScoreResponse":
        return cls(
            id=score.id,
            student_id=score.student_id,
            month=score.month,
            subject=score.subject.value,
            score=str(score.score),
            updated_at=score.updated_at.isoformat(),
        )
