from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


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


def test_list_students_has_no_create_side_effect() -> None:
    first = client.get("/api/v1/students")
    second = client.get("/api/v1/students")
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"] == second.json()["data"] == []


def test_list_students_rejects_mutation_query_params() -> None:
    response = client.get("/api/v1/students", params={"score": "99"})
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "VALIDATION_ERROR"
    assert "read-only" in detail["message"]
