from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # required for sessions

DB_FILE = "attendance.db"

# Create database if it doesn't exist
def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                name TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

init_db()


@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    error = None

    if request.method == "POST":
        student_id = request.form.get("student_id")
        name = request.form.get("name")

        if student_id and name:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO attendance (student_id, name) VALUES (?, ?)", (student_id, name))
            conn.commit()
            conn.close()
            message = f"✅ {name} (ID: {student_id}) checked in successfully!"
        else:
            error = "⚠ Please enter both Student ID and Name."

    return render_template("index.html", message=message, error=error)


@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    # Password for teachers/admins
    ADMIN_PASSWORD = "admin123"

    # If not logged in, ask for password
    if "logged_in" not in session:
        if request.method == "POST":
            password = request.form.get("password")
            if password == ADMIN_PASSWORD:
                session["logged_in"] = True
                return redirect(url_for("attendance"))
            else:
                return render_template("login.html", error="❌ Wrong password!")
        return render_template("login.html")

    # If logged in, show records
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT student_id, name, timestamp FROM attendance ORDER BY timestamp DESC")
    records = c.fetchall()
    conn.close()

    return render_template("attendance.html", records=records)


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
