from fastapi.testclient import TestClient

from backend.main import app
from backend.src.api import student_scores as api_module
from backend.src.services.student_score_service import StudentScoreService

client = TestClient(app)


def setup_function() -> None:
    api_module.service = StudentScoreService()


def _create(student_no: str) -> dict:
    response = client.post(
        "/api/v1/students",
        json={"studentNo": student_no, "name": "张三", "gender": "male"},
    )
    return response.json()["data"]


def test_update_student_success() -> None:
    student = _create("S001")
    response = client.put(
        f"/api/v1/students/{student['id']}",
        json={
            "studentNo": "S001",
            "name": "李四",
            "gender": "female",
            "updatedAt": student["updated_at"],
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "李四"


def test_update_student_version_conflict_returns_409() -> None:
    student = _create("S001")
    response = client.put(
        f"/api/v1/students/{student['id']}",
        json={
            "studentNo": "S001",
            "name": "李四",
            "gender": "female",
            "updatedAt": "2000-01-01T00:00:00",
        },
    )
    assert response.status_code == 409


def test_update_student_no_conflict_returns_409() -> None:
    first = _create("S001")
    _create("S002")
    response = client.put(
        f"/api/v1/students/{first['id']}",
        json={
            "studentNo": "S002",
            "name": "李四",
            "gender": "female",
            "updatedAt": first["updated_at"],
        },
    )
    assert response.status_code == 409
