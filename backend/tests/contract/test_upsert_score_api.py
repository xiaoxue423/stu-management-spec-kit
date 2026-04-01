from fastapi.testclient import TestClient

from backend.main import app
from backend.src.api import student_scores as api_module
from backend.src.services.student_score_service import StudentScoreService

client = TestClient(app)


def setup_function() -> None:
    api_module.service = StudentScoreService()


def _create_student() -> int:
    response = client.post(
        "/api/v1/students",
        json={"studentNo": "S001", "name": "张三", "gender": "male"},
    )
    return response.json()["data"]["id"]


def test_upsert_score_success() -> None:
    student_id = _create_student()
    response = client.post(
        f"/api/v1/students/{student_id}/scores",
        json={"month": 3, "subject": "math", "score": "89.50"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["score"] == "89.50"


def test_upsert_score_out_of_range_returns_400() -> None:
    student_id = _create_student()
    response = client.post(
        f"/api/v1/students/{student_id}/scores",
        json={"month": 3, "subject": "math", "score": 120},
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "VALIDATION_ERROR"


def test_upsert_score_precision_returns_400() -> None:
    student_id = _create_student()
    response = client.post(
        f"/api/v1/students/{student_id}/scores",
        json={"month": 3, "subject": "math", "score": "88.888"},
    )
    assert response.status_code == 400
