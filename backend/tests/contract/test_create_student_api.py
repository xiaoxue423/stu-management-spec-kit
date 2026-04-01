from fastapi.testclient import TestClient

from backend.main import app
from backend.src.api import student_scores as api_module
from backend.src.services.student_score_service import StudentScoreService

client = TestClient(app)


def setup_function() -> None:
    api_module.service = StudentScoreService()


def test_create_student_success() -> None:
    response = client.post(
        "/api/v1/students",
        json={"studentNo": "S001", "name": "张三", "gender": "male"},
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["student_no"] == "S001"
    assert body["name"] == "张三"


def test_create_student_duplicate_student_no_returns_409() -> None:
    payload = {"studentNo": "S001", "name": "张三", "gender": "male"}
    client.post("/api/v1/students", json=payload)

    response = client.post("/api/v1/students", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "CONFLICT"


def test_create_student_missing_required_returns_400() -> None:
    response = client.post("/api/v1/students", json={"studentNo": "", "gender": "male"})
    assert response.status_code == 400
