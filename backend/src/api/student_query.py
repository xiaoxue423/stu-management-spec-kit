from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.src.db.deps import get_db
from backend.src.schemas.student import StudentResponse
from backend.src.services.errors import DomainError
from backend.src.services.student_score_service_factory import get_student_score_service

router = APIRouter(prefix="/api/v1/students", tags=["students-query"])
_MUTATION_QUERY_KEYS = {"month", "subject", "score", "updatedAt"}


def _raise_http(exc: DomainError) -> None:
    raise HTTPException(status_code=exc.status_code, detail={"code": exc.error_code, "message": exc.message})


def _raise_unknown() -> None:
    raise HTTPException(status_code=500, detail={"code": "UNKNOWN_ERROR", "message": "internal server error"})


@router.get("")
def list_students(request: Request, db: Session = Depends(get_db)) -> dict:
    mutation_keys = sorted(_MUTATION_QUERY_KEYS.intersection(set(request.query_params.keys())))
    if mutation_keys:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "VALIDATION_ERROR",
                "message": f"list endpoint is read-only, unsupported query params: {','.join(mutation_keys)}",
            },
        )
    try:
        svc = get_student_score_service(db)
        students = svc.list_students()
        return {"data": [StudentResponse.from_model(s) for s in students]}
    except DomainError as exc:
        _raise_http(exc)
    except Exception:
        _raise_unknown()
