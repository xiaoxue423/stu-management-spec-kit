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
        json={"name": "张三", "gender": "male"},
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["student_no"] == "0001"
    assert body["name"] == "张三"


def test_create_student_auto_number_increments() -> None:
    first = client.post("/api/v1/students", json={"name": "张三", "gender": "male"})
    second = client.post("/api/v1/students", json={"name": "李四", "gender": "female"})
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["student_no"] == "0001"
    assert second.json()["data"]["student_no"] == "0002"


def test_create_student_exhausted_student_no_returns_409() -> None:
    # 覆盖上限场景，避免循环创建 9999 条测试数据。
    api_module.service._student_no_seq = 10000
    response = client.post("/api/v1/students", json={"name": "张三", "gender": "male"})
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "CONFLICT"


def test_create_student_missing_required_returns_400() -> None:
    response = client.post("/api/v1/students", json={"gender": "male"})
    assert response.status_code == 400
