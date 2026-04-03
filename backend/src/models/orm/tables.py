"""ORM tables: students, exam_scores, student_no_seq."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, ForeignKey, Integer, Numeric, SmallInteger, String, TinyInteger, UniqueConstraint
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.src.db.base import Base


class StudentNoSeqRow(Base):
    __tablename__ = "student_no_seq"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=False)
    next_val: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")


class StudentRow(Base):
    __tablename__ = "students"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    student_no: Mapped[str] = mapped_column(String(4), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6), nullable=False)

    scores: Mapped[list["ExamScoreRow"]] = relationship(
        "ExamScoreRow",
        back_populates="student",
        passive_deletes=True,
    )


class ExamScoreRow(Base):
    __tablename__ = "exam_scores"
    __table_args__ = (
        UniqueConstraint("student_id", "month", "subject", name="uq_exam_scores_student_month_subject"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("students.id", ondelete="RESTRICT"),
        nullable=False,
    )
    month: Mapped[int] = mapped_column(TinyInteger, nullable=False)
    subject: Mapped[str] = mapped_column(String(32), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DATETIME(fsp=6), nullable=False)

    student: Mapped["StudentRow"] = relationship("StudentRow", back_populates="scores")
