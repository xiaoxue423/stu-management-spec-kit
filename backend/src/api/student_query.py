from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from backend.src.api import student_scores as score_api
from backend.src.schemas.student import StudentResponse
from backend.src.services.student_score_service import DomainError

router = APIRouter(prefix="/api/v1/students", tags=["students-query"])
_MUTATION_QUERY_KEYS = {"month", "subject", "score", "updatedAt"}


def _raise_http(exc: DomainError) -> None:
    raise HTTPException(status_code=exc.status_code, detail={"code": exc.error_code, "message": exc.message})


def _raise_unknown() -> None:
    raise HTTPException(status_code=500, detail={"code": "UNKNOWN_ERROR", "message": "internal server error"})


@router.get("")
def list_students(request: Request) -> dict:
    # 查询接口职责：只读，不接收任何带写入语义的参数。
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
        students = score_api.service.list_students()
        return {"data": [StudentResponse.from_model(s) for s in students]}
    except DomainError as exc:
        _raise_http(exc)
    except Exception:
        _raise_unknown()
