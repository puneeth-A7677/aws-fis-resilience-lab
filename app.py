from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "resilience.db"


def init_database():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_name TEXT NOT NULL,
            result TEXT NOT NULL,
            recovery_notes TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def get_experiments():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    experiments = conn.execute("""
        SELECT * FROM experiments
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return experiments


@app.route("/")
def home():
    experiments = get_experiments()

    database_status = "CONNECTED"

    return render_template(
        "index.html",
        experiments=experiments,
        database_status=database_status
    )


@app.route("/save", methods=["POST"])
def save_experiment():
    experiment_name = request.form["experiment_name"]
    result = request.form["result"]
    recovery_notes = request.form["recovery_notes"]

    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        INSERT INTO experiments
        (experiment_name, result, recovery_notes, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        experiment_name,
        result,
        recovery_notes,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/health")
def health():
    try:
        conn = sqlite3.connect(DATABASE)
        conn.execute("SELECT 1")
        conn.close()

        return {
            "backend": "ONLINE",
            "database": "CONNECTED",
            "status": "HEALTHY"
        }

    except Exception as error:
        return {
            "backend": "ONLINE",
            "database": "ERROR",
            "status": str(error)
        }, 500


if __name__ == "__main__":
    init_database()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
