"""Student rows: sequence, CRUD, optimistic updates."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select, text, update
from sqlalchemy.orm import Session

from backend.src.models.orm.tables import StudentRow
from backend.src.models.student import Gender, Student
from backend.src.services.errors import ConflictError, NotFoundError


class StudentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def allocate_next_student_no(self) -> str:
        self._session.execute(
            text("UPDATE student_no_seq SET next_val = LAST_INSERT_ID(next_val + 1) WHERE id = 1")
        )
        row = self._session.execute(text("SELECT LAST_INSERT_ID() AS n")).mappings().one()
        n = int(row["n"])
        if n > 9999:
            raise ConflictError("student_no range exhausted")
        return f"{n:04d}"

    def insert_student(self, *, student_no: str, name: str, gender: Gender, now: datetime) -> Student:
        row = StudentRow(
            student_no=student_no,
            name=name,
            gender=gender.value,
            created_at=now,
            updated_at=now,
        )
        self._session.add(row)
        self._session.flush()
        return self._to_domain(row)

    def get_by_id(self, student_id: int) -> Student | None:
        row = self._session.get(StudentRow, student_id)
        return self._to_domain(row) if row else None

    def list_sorted_by_id(self) -> list[Student]:
        result = self._session.execute(select(StudentRow).order_by(StudentRow.id.asc()))
        rows = result.scalars().all()
        return [self._to_domain(r) for r in rows]

    def update_if_version_matches(
        self,
        student_id: int,
        *,
        name: str,
        gender: Gender,
        expected_updated_at: datetime,
        now: datetime,
    ) -> Student:
        stmt = (
            update(StudentRow)
            .where(StudentRow.id == student_id, StudentRow.updated_at == expected_updated_at)
            .values(name=name, gender=gender.value, updated_at=now)
        )
        res = self._session.execute(stmt)
        if res.rowcount != 1:
            exists = self._session.get(StudentRow, student_id)
            if not exists:
                raise NotFoundError("student not found")
            raise ConflictError("student version conflict")
        row = self._session.get(StudentRow, student_id)
        assert row is not None
        return self._to_domain(row)

    @staticmethod
    def _to_domain(row: StudentRow) -> Student:
        return Student(
            id=row.id,
            student_no=row.student_no,
            name=row.name,
            gender=Gender(row.gender),
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
