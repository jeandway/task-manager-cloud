import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DATABASE = "tasks.db"

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

def init_db():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL
        );
        """
    )

    connection.commit()
    connection.close()

@app.route("/")
def index():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, title, description, status FROM tasks;")
    rows = cursor.fetchall()

    tasks = []
    for row in rows:
        task = {
            "id": row["id"],
            "title": row["title"],
            "description": row["description"],
            "status": row["status"]
        }
        tasks.append(task)

    connection.close()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        status = request.form.get("status")

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO tasks (title, description, status) VALUES (?, ?, ?);",
            (title, description, status)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("index"))

    return render_template("add.html")

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, title, description, status FROM tasks WHERE id = ?;",
        (task_id,)
    )
    row = cursor.fetchone()

    if row is None:
        connection.close()
        return "Task not found", 404

    task = {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "status": row["status"]
    }

    if request.method == "POST":
        new_title = request.form.get("title")
        new_description = request.form.get("description")
        new_status = request.form.get("status")

        cursor.execute(
            "UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ?;",
            (new_title, new_description, new_status, task_id)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("index"))

    connection.close()
    return render_template("edit.html", task=task)

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
    connection.commit()
    connection.close()

    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
