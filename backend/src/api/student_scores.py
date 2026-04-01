from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.src.models.exam_score import Subject
from backend.src.models.student import Gender
from backend.src.schemas.score import ScoreResponse, UpsertScoreRequest
from backend.src.schemas.student import CreateStudentRequest, StudentResponse, UpdateStudentRequest
from backend.src.services.student_score_service import DomainError, StudentScoreService

router = APIRouter(prefix="/api/v1/students", tags=["students"])
service = StudentScoreService()


class CreateStudentBody(BaseModel):
    name: str
    gender: Gender


class UpdateStudentBody(BaseModel):
    name: str
    gender: Gender
    updatedAt: datetime


class UpsertScoreBody(BaseModel):
    month: int
    subject: Subject
    score: Decimal


def _raise_http(exc: DomainError) -> None:
    raise HTTPException(status_code=exc.status_code, detail={"code": exc.error_code, "message": exc.message})


def _raise_unknown() -> None:
    raise HTTPException(status_code=500, detail={"code": "UNKNOWN_ERROR", "message": "internal server error"})


@router.post("")
def create_student(body: CreateStudentBody) -> dict:
    try:
        student = service.create_student(CreateStudentRequest(name=body.name, gender=body.gender))
        return {"data": StudentResponse.from_model(student)}
    except DomainError as exc:
        _raise_http(exc)
    except Exception:
        _raise_unknown()


@router.get("")
def list_students() -> dict:
    try:
        students = service.list_students()
        return {"data": [StudentResponse.from_model(s) for s in students]}
    except DomainError as exc:
        _raise_http(exc)
    except Exception:
        _raise_unknown()


@router.put("/{student_id}")
def update_student(student_id: int, body: UpdateStudentBody) -> dict:
    try:
        student = service.update_student(
            student_id,
            UpdateStudentRequest(
                name=body.name,
                gender=body.gender,
                updated_at=body.updatedAt,
            ),
        )
        return {"data": StudentResponse.from_model(student)}
    except DomainError as exc:
        _raise_http(exc)
    except Exception:
        _raise_unknown()


@router.post("/{student_id}/scores")
def upsert_score(student_id: int, body: UpsertScoreBody) -> dict:
    try:
        score = service.upsert_score(
            student_id, UpsertScoreRequest(month=body.month, subject=body.subject, score=body.score)
        )
        return {"data": ScoreResponse.from_model(score)}
    except DomainError as exc:
        _raise_http(exc)
    except Exception:
        _raise_unknown()


@router.get("/{student_id}/edit-form")
def get_edit_form(student_id: int) -> dict:
    try:
        edit_form = service.get_edit_form(student_id)
        return {
            "data": {
                "student": StudentResponse.from_model(edit_form.student),
                "scores": [ScoreResponse.from_model(s) for s in edit_form.scores],
            }
        }
    except DomainError as exc:
        _raise_http(exc)
    except Exception:
        _raise_unknown()
