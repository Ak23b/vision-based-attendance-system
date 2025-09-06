from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"
DB_FILE = "attendance.db"


# Initialize DB
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Attendance table
    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()


# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def index():
    message, error = None, None
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


@app.route("/attendance")
def attendance():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT student_id, name, timestamp FROM attendance ORDER BY timestamp DESC")
    records = c.fetchall()
    conn.close()
    return render_template("attendance.html", records=records, user=session["user"])


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        conn.close()

        if result and check_password_hash(result[0], password):
            session["user"] = username
            return redirect(url_for("attendance"))
        else:
            error = "❌ Invalid username or password."
    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_pw = generate_password_hash(password)

        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            error = "⚠ Username already exists."
    return render_template("register.html", error=error)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
