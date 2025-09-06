import sqlite3

conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# Create table for admin credentials
cursor.execute('''
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
''')

# Insert default admin (optional: only first time)
cursor.execute("INSERT OR IGNORE INTO admin (username, password) VALUES (?, ?)", ("admin", "admin123"))

conn.commit()
conn.close()

print("Admin table ready. Default username=admin, password=admin123")
