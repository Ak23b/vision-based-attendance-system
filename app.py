import os
import sqlite3
from flask import Flask, request, render_template
import cv2

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

# Make sure uploads folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ========== Database Setup ==========
def init_db():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ========== Face Detection ==========
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def detect_face(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    return len(faces) > 0

# ========== Routes ==========
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files or "name" not in request.form:
        return "No file or name provided", 400

    file = request.files["file"]
    name = request.form["name"]

    if file.filename == "":
        return "No selected file", 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # Run face detection
    if detect_face(filepath):
        conn = sqlite3.connect("attendance.db")
        c = conn.cursor()
        c.execute("INSERT INTO attendance (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        msg = f"✅ Attendance marked for {name}"
    else:
        msg = "⚠️ No face detected, try again."

    return render_template("index.html", message=msg)

@app.route("/attendance")
def attendance():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("SELECT name, timestamp FROM attendance ORDER BY timestamp DESC")
    records = c.fetchall()
    conn.close()
    return render_template("attendance.html", records=records)

if __name__ == "__main__":
    app.run(debug=True)
