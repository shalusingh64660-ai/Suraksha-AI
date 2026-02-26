from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app)

DATABASE = "database.db"

# -------------------------------
# EMAIL CONFIG (USE APP PASSWORD)
# -------------------------------
SENDER_EMAIL = "suraksha012345@gmail.com"
SENDER_PASSWORD = "gftshisyndkygbdj"

# -------------------------------
# DATABASE INIT
# -------------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emergency_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sos_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        latitude TEXT,
        longitude TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------------
# HOME
# -------------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -------------------------------
# ADD EMERGENCY CONTACT
# -------------------------------
@app.route("/add_emergency_contact", methods=["POST"])
def add_emergency_contact():
    data = request.json
    name = data.get("name")
    email = data.get("email")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO emergency_contacts (name, email) VALUES (?, ?)",
        (name, email)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Emergency contact added successfully!"})


# -------------------------------
# SOS ROUTE
# -------------------------------
@app.route("/sos", methods=["POST"])
def sos():
    data = request.json

    user = data.get("user")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Save log
    cursor.execute(
        "INSERT INTO sos_logs (user, latitude, longitude) VALUES (?, ?, ?)",
        (user, latitude, longitude)
    )

    cursor.execute("SELECT email FROM emergency_contacts")
    emails = cursor.fetchall()

    conn.commit()
    conn.close()

    if not emails:
        return jsonify({"message": "No emergency contacts found"}), 400

    subject = "🚨 EMERGENCY ALERT - Suraksha AI"

    body = f"""
🚨 EMERGENCY ALERT 🚨

User: {user}

Live Location:
https://www.google.com/maps?q={latitude},{longitude}

Please respond immediately.
"""

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        for email in emails:
            receiver = email[0]

            # ✅ Skip invalid or empty emails
            if not receiver or "@" not in receiver:
                print("⚠ Skipping invalid email:", receiver)
                continue

            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = SENDER_EMAIL
            msg["To"] = receiver

            server.sendmail(SENDER_EMAIL, receiver, msg.as_string())
            print("✅ Email sent to:", receiver)

        server.quit()

    except Exception as e:
        print("❌ Email Error:", e)
        return jsonify({"message": "Email sending failed", "error": str(e)}), 500

    return jsonify({"message": "🚨 SOS Sent Successfully!"})

# -------------------------------
# VIEW CONTACTS
# -------------------------------
@app.route("/view_contacts")
def view_contacts():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emergency_contacts")
    contacts = cursor.fetchall()
    conn.close()
    return jsonify(contacts)


# -------------------------------
# VIEW LOGS
# -------------------------------
@app.route("/view_logs")
def view_logs():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sos_logs")
    logs = cursor.fetchall()
    conn.close()
    return jsonify(logs)


if __name__ == "__main__":
    app.run(debug=True)