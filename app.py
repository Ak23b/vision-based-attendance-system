from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"  # required for sessions

# ---------- Helper functions ----------
def get_db_connection():
    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------- Login ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        admin = conn.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()

        if admin:
            session["admin"] = username
            return redirect(url_for("attendance_log"))
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html")

# ---------- Attendance Log (Protected) ----------
@app.route("/attendance")
def attendance_log():
    if "admin" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    records = conn.execute("SELECT * FROM attendance").fetchall()
    conn.close()
    return render_template("attendance.html", records=records)

# ---------- Password Settings ----------
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "admin" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        new_username = request.form["username"]
        new_password = request.form["password"]

        conn = get_db_connection()
        conn.execute("UPDATE admin SET username=?, password=? WHERE id=1", (new_username, new_password))
        conn.commit()
        conn.close()

        flash("Credentials updated successfully!", "success")
        return redirect(url_for("settings"))

    return render_template("settings.html")

# ---------- Logout ----------
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
