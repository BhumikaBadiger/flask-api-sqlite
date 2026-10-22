
import pytest
from app import app, init_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Give each test its own temporary SQLite database.
    db_file = tmp_path / "test_tasks.db"
    monkeypatch.setattr("app.DB_NAME", str(db_file))

    init_db()

    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_create_and_get_task(client):
    response = client.post(
        "/tasks",
        json={"title": "Learn CI/CD"}
    )

    assert response.status_code == 201
    task = response.get_json()
    assert task["title"] == "Learn CI/CD"
    assert task["completed"] is False

    task_id = task["id"]
    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.get_json()["title"] == "Learn CI/CD"


def test_reject_empty_title(client):
    response = client.post("/tasks", json={"title": "  "})

    assert response.status_code == 400


def test_delete_task(client):
    created = client.post("/tasks", json={"title": "Temporary task"})
    task_id = created.get_json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert client.get(f"/tasks/{task_id}").status_code == 404
