from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
import csv
import io
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()

    # Attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            timestamp TEXT
        )
    """)

    # --- Migration: Add student_id column if missing ---
    cursor.execute("PRAGMA table_info(attendance)")
    columns = [col[1] for col in cursor.fetchall()]
    if "student_id" not in columns:
        cursor.execute("ALTER TABLE attendance ADD COLUMN student_id TEXT")

    # Admins table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Insert default admin if none exists
    cursor.execute("SELECT * FROM admins")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", ("admin", "admin123"))
    
    conn.commit()
    conn.close()

init_db()

# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        student_id = request.form["student_id"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect("attendance.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO attendance (name, student_id, timestamp) VALUES (?, ?, ?)",
                       (name, student_id, timestamp))
        conn.commit()
        conn.close()

        return f"{name} (ID: {student_id}) checked in at {timestamp}"
    return render_template("index.html")

@app.route("/attendance")
def attendance():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, student_id, timestamp FROM attendance ORDER BY timestamp DESC")
    records = cursor.fetchall()
    conn.close()

    return render_template("attendance.html", records=records)

# ---------- Other routes (login, logout, settings, exports, etc.) remain the same ----------
if __name__ == "__main__":
    app.run(debug=True)
