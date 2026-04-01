from fastapi.testclient import TestClient

from backend.main import app
from backend.src.api import student_scores as api_module
from backend.src.services.student_score_service import StudentScoreService

client = TestClient(app)


def setup_function() -> None:
    api_module.service = StudentScoreService()


def _create() -> dict:
    response = client.post(
        "/api/v1/students",
        json={"name": "张三", "gender": "male"},
    )
    return response.json()["data"]


def test_update_student_success() -> None:
    student = _create()
    response = client.put(
        f"/api/v1/students/{student['id']}",
        json={
            "name": "李四",
            "gender": "female",
            "updatedAt": student["updated_at"],
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "李四"


def test_update_student_version_conflict_returns_409() -> None:
    student = _create()
    response = client.put(
        f"/api/v1/students/{student['id']}",
        json={
            "name": "李四",
            "gender": "female",
            "updatedAt": "2000-01-01T00:00:00",
        },
    )
    assert response.status_code == 409


def test_update_student_keeps_student_no_unchanged() -> None:
    first = _create()
    response = client.put(
        f"/api/v1/students/{first['id']}",
        json={
            "name": "李四",
            "gender": "female",
            "updatedAt": first["updated_at"],
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["student_no"] == first["student_no"]
