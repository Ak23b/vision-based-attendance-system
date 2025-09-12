from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime, time

app = Flask(__name__)
app.secret_key = "your_secret_key"
DB_NAME = "attendance.db"

CLASS_START_TIME = time(9, 0)  # default 9:00 AM

# ---------- INIT DB ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Students table (now with class_name)
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    class_name TEXT)''')

    # Attendance table
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT,
                    name TEXT,
                    class_name TEXT,
                    class_date DATE,
                    sign_in_time TIME,
                    status TEXT,
                    FOREIGN KEY(student_id) REFERENCES students(student_id))''')

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT)''')

    # Add default admin if not exists
    c.execute("SELECT * FROM users WHERE username=?", ("admin",))
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))

    conn.commit()
    conn.close()


# Ensure tables are created on startup
init_db()

# ---------- STUDENT CHECK-IN ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        student_id = request.form["student_id"]
        name = request.form["name"]
        class_name = request.form["class_name"]   # ✅ new field

        today = datetime.now().date()
        now_time = datetime.now().time()

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        # Save student info (with class_name) if not already in table
        c.execute("""INSERT OR REPLACE INTO students (student_id, name, class_name)
                     VALUES (?, ?, ?)""", (student_id, name, class_name))

        # Insert attendance record
        c.execute("""INSERT INTO attendance (student_id, name, class_name, class_date, sign_in_time, status)
                     VALUES (?, ?, ?, ?, ?, NULL)""",
                  (student_id, name, class_name, today, now_time.strftime("%H:%M:%S")))

        conn.commit()
        conn.close()

        return render_template("index.html", message=f"{name} checked in for {class_name}!")

    return render_template("index.html")


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("attendance"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


# ---------- REGISTER NEW ADMIN ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            return render_template("register.html", message="New admin created successfully!")
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("register.html", error="Username already exists!")

    return render_template("register.html")


# ---------- SETTINGS (Change Password) ----------
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (session["username"], old_password))
        user = c.fetchone()

        if user:
            c.execute("UPDATE users SET password=? WHERE username=?", (new_password, session["username"]))
            conn.commit()
            conn.close()
            return render_template("settings.html", message="Password updated successfully!")
        else:
            conn.close()
            return render_template("settings.html", error="Old password is incorrect.")

    return render_template("settings.html")


# ---------- ATTENDANCE DASHBOARD ----------
@app.route("/attendance")
def attendance():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    today = datetime.now().date()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT student_id, name, class_name, sign_in_time FROM attendance WHERE class_date=?", (today,))
    rows = c.fetchall()
    conn.close()

    return render_template("attendance.html", rows=rows, today=today)


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    session.pop("username", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
