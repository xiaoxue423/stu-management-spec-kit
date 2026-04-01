from fastapi.testclient import TestClient

from backend.main import app
from backend.src.api import student_scores as api_module
from backend.src.services.student_score_service import StudentScoreService

client = TestClient(app)


def setup_function() -> None:
    api_module.service = StudentScoreService()


def test_list_students_empty() -> None:
    response = client.get("/api/v1/students")
    assert response.status_code == 200
    assert response.json()["data"] == []


def test_list_students_after_create() -> None:
    client.post(
        "/api/v1/students",
        json={"name": "张三", "gender": "male"},
    )

    response = client.get("/api/v1/students")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
