from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("todo.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------- BACKEND STATUS ----------------
@app.route("/backend-status")
def backend_status():
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
        return {"server": "Running", "database": "Connected", "status": "Healthy"}
    except Exception as e:
        return {"server": "Running", "database": "Error", "status": "Unhealthy", "error": str(e)}

# ---------------- HOME ----------------
@app.route("/")
def index():
    conn = get_db()
    tasks = conn.execute(
        "SELECT * FROM tasks ORDER BY created_at DESC"
    ).fetchall()
    conn.close()

    status = {"server": "Running", "database": "Connected"}
    return render_template("index.html", tasks=tasks, backend_status=status)

# ---------------- ADD TASK ----------------
@app.route("/add", methods=["POST"])
def add():
    title = request.form["title"]
    description = request.form["description"]
    due_date = request.form["due_date"]
    priority = request.form["priority"]
    status = request.form["status"]

    conn = get_db()
    conn.execute("""
        INSERT INTO tasks (title, description, due_date, priority, status)
        VALUES (?, ?, ?, ?, ?)
    """, (title, description, due_date, priority, status))
    conn.commit()
    conn.close()

    return redirect(url_for("index"))

# ---------------- EDIT TASK ----------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        due_date = request.form["due_date"]
        priority = request.form["priority"]
        status = request.form["status"]

        conn.execute("""
            UPDATE tasks
            SET title=?, description=?, due_date=?, priority=?, status=?
            WHERE id=?
        """, (title, description, due_date, priority, status, id))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    task = conn.execute("SELECT * FROM tasks WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit.html", task=task)

# ---------------- DELETE TASK ----------------
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# ---------------- INIT DB ----------------
if __name__ == "__main__":
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            priority TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.close()

    app.run(debug=True)
