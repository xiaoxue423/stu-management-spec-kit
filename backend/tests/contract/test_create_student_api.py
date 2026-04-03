from sqlalchemy import text

from fastapi.testclient import TestClient

from backend.main import app
from backend.src.db.session import SessionLocal

client = TestClient(app)


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
    """Next sequence value 10000 must return CONFLICT (autouse reset runs before this test)."""
    db = SessionLocal()
    try:
        db.execute(text("UPDATE student_no_seq SET next_val = 9999 WHERE id = 1"))
        db.commit()
    finally:
        db.close()
    response = client.post("/api/v1/students", json={"name": "张三", "gender": "male"})
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "CONFLICT"


def test_create_student_missing_required_returns_400() -> None:
    response = client.post("/api/v1/students", json={"gender": "male"})
    assert response.status_code == 400


def test_create_student_without_score_and_then_edit_form_has_empty_scores() -> None:
    created = client.post("/api/v1/students", json={"name": "王五", "gender": "male"})
    assert created.status_code == 200
    student_id = created.json()["data"]["id"]

    edit_form = client.get(f"/api/v1/students/{student_id}/edit-form")
    assert edit_form.status_code == 200
    assert edit_form.json()["data"]["scores"] == []


def test_create_student_contract_is_write_only_boundary() -> None:
    response = client.post("/api/v1/students", json={"name": "赵六", "gender": "female"})
    assert response.status_code == 200
    body = response.json()
    assert "data" in body
    assert "total" not in body
    assert "items" not in body
