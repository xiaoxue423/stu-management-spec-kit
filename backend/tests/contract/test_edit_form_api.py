from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_get_edit_form_not_found() -> None:
    response = client.get("/api/v1/students/999/edit-form")
    assert response.status_code == 404


def test_get_edit_form_success() -> None:
    created = client.post(
        "/api/v1/students",
        json={"name": "张三", "gender": "male"},
    ).json()["data"]
    client.post(
        f"/api/v1/students/{created['id']}/scores",
        json={"month": 6, "subject": "math", "score": "92.50"},
    )

    response = client.get(f"/api/v1/students/{created['id']}/edit-form")
    assert response.status_code == 200
    assert response.json()["data"]["student"]["id"] == created["id"]
    assert len(response.json()["data"]["scores"]) == 1
