
import pytest
from app import app, init_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test_tasks.db"
    monkeypatch.setattr("app.DB_NAME", str(db_file))
    init_db()

    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def create_task(client, title="Learn CI/CD"):
    response = client.post("/tasks", json={"title": title})
    assert response.status_code == 201
    return response.get_json()


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}


def test_create_and_get_task(client):
    task = create_task(client)

    assert task["title"] == "Learn CI/CD"
    assert task["completed"] is False

    response = client.get(f"/tasks/{task['id']}")
    assert response.status_code == 200
    assert response.get_json() == task


def test_list_tasks(client):
    first = create_task(client, "First task")
    second = create_task(client, "Second task")

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.get_json() == [first, second]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": ""},
        {"title": "   "},
        {"title": 123},
        {"title": None},
    ],
)
def test_reject_invalid_task_title(client, payload):
    response = client.post("/tasks", json=payload)
    assert response.status_code == 400


def test_reject_malformed_json(client):
    response = client.post(
        "/tasks",
        data='{"title":',
        content_type="application/json",
    )
    assert response.status_code == 400


def test_update_task_title_and_completion(client):
    task = create_task(client, "Original title")

    response = client.put(
        f"/tasks/{task['id']}",
        json={"title": "Updated title", "completed": True},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "id": task["id"],
        "title": "Updated title",
        "completed": True,
    }

    fetched = client.get(f"/tasks/{task['id']}")
    assert fetched.get_json()["title"] == "Updated title"
    assert fetched.get_json()["completed"] is True


def test_update_only_completion(client):
    task = create_task(client, "Keep this title")

    response = client.put(
        f"/tasks/{task['id']}",
        json={"completed": True},
    )

    assert response.status_code == 200
    assert response.get_json()["title"] == "Keep this title"
    assert response.get_json()["completed"] is True


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": "   "},
        {"completed": "true"},
        {"completed": 1},
        {"priority": "high"},
    ],
)
def test_reject_invalid_update(client, payload):
    task = create_task(client)
    response = client.put(f"/tasks/{task['id']}", json=payload)
    assert response.status_code == 400


def test_get_missing_task_returns_404(client):
    response = client.get("/tasks/9999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Task not found"}


def test_update_missing_task_returns_404(client):
    response = client.put("/tasks/9999", json={"completed": True})
    assert response.status_code == 404


def test_delete_task(client):
    task = create_task(client, "Temporary task")

    response = client.delete(f"/tasks/{task['id']}")
    assert response.status_code == 200
    assert response.get_json() == {"message": "Task deleted"}

    assert client.get(f"/tasks/{task['id']}").status_code == 404


def test_delete_missing_task_returns_404(client):
    response = client.delete("/tasks/9999")
    assert response.status_code == 404
