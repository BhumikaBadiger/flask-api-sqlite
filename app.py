
from flask import Flask, request, jsonify
import sqlite3
from contextlib import contextmanager

app = Flask(__name__)
DB_NAME = "tasks.db"


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
        """)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/tasks", methods=["GET"])
def get_tasks():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, title, completed FROM tasks ORDER BY id"
        ).fetchall()

    result = [
        {
            "id": row["id"],
            "title": row["title"],
            "completed": bool(row["completed"])
        }
        for row in rows
    ]

    return jsonify(result), 200


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, title, completed FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

    if row is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({
        "id": row["id"],
        "title": row["title"],
        "completed": bool(row["completed"])
    }), 200


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True)

    if (
        not isinstance(data, dict)
        or not isinstance(data.get("title"), str)
        or not data["title"].strip()
    ):
        return jsonify({
            "error": "A non-empty title is required"
        }), 400

    title = data["title"].strip()

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (title,)
        )
        task_id = cursor.lastrowid

    return jsonify({
        "id": task_id,
        "title": title,
        "completed": False
    }), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({"error": "A JSON object is required"}), 400

    if "title" not in data and "completed" not in data:
        return jsonify({"error": "No fields to update"}), 400

    if "title" in data and (
        not isinstance(data["title"], str)
        or not data["title"].strip()
    ):
        return jsonify({"error": "Title cannot be empty"}), 400

    if "completed" in data and not isinstance(data["completed"], bool):
        return jsonify({
            "error": "completed must be a boolean"
        }), 400

    with get_db() as conn:
        row = conn.execute(
            "SELECT id, title, completed FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        if row is None:
            return jsonify({"error": "Task not found"}), 404

        title = data.get("title", row["title"])
        if "title" in data:
            title = title.strip()

        completed = data.get("completed", bool(row["completed"]))

        conn.execute(
            "UPDATE tasks SET title = ?, completed = ? WHERE id = ?",
            (title, int(completed), task_id)
        )

    return jsonify({
        "id": task_id,
        "title": title,
        "completed": completed
    }), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

    return jsonify({"message": "Task deleted"}), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
