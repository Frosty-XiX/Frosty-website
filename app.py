from flask import Flask, request, render_template, jsonify
import sqlite3
import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT,
                    last_seen TEXT,
                    ip TEXT,
                    battery TEXT,
                    location TEXT
                )''')
    conn.commit()
    conn.close()

@app.route('/')
def dashboard():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM devices")
    devices = c.fetchall()
    conn.close()
    return render_template("dashboard.html", devices=devices)

@app.route('/api/report', methods=['POST'])
def report():
    data = request.json
    device_id = data.get("device_id")
    battery = data.get("battery")
    location = data.get("location")
    ip = request.remote_addr
    last_seen = datetime.datetime.now().isoformat()

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
    if c.fetchone():
        c.execute("UPDATE devices SET last_seen=?, ip=?, battery=?, location=? WHERE device_id=?",
                  (last_seen, ip, battery, location, device_id))
    else:
        c.execute("INSERT INTO devices (device_id, last_seen, ip, battery, location) VALUES (?, ?, ?, ?, ?)",
                  (device_id, last_seen, ip, battery, location))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
