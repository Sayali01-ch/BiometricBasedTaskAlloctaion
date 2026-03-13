import logging
import os
import json
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit
import db
import fcm
import adms_parser

app = Flask(__name__)
app.config['SECRET_KEY'] = 'biometric-dev'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Port
APP_PORT = int(os.getenv("PORT", 8000))

# Init
db = db.Database('app.db')
fcm_client = fcm.FcmClient()

print(f"✅ DB ready: {db.path}")
print(f"{'✅' if fcm_client.enabled else '⚠️'} FCM: {fcm_client.init_error or 'enabled'}")

@app.route('/')
def dashboard():
    return render_template('dashboard.html', fcm_enabled=fcm_client.enabled, fcm_error=fcm_client.init_error)

@app.route('/dashboard')
def dashboard_redirect():
    return render_template('dashboard.html', fcm_enabled=fcm_client.enabled, fcm_error=fcm_client.init_error)

@app.route('/status')
def status():
    return jsonify({"status": "online", "port": APP_PORT})

@app.route('/metrics')
def metrics():
    return jsonify({
        "uptime": "1",  # Stub for Prometheus
        "requests_total": 42,
        "active_connections": len(socketio.server.environ or []),
        "fcm_enabled": fcm_client.enabled
    })  # Scale: Integrate prometheus_client

@app.route('/api/employees')
def list_employees():
    return jsonify({"employees": db.list_employees()})

@app.route('/api/today_attendance')
def today_attendance():
    from datetime import date
    today = date.today().isoformat()
    employees = db.list_employees()
    today_emps = [emp for emp in employees if emp.get('last_seen_at', '').startswith(today)]
    return jsonify({"today_attendance": today_emps, "today_count": len(today_emps)})


@app.route('/api/tasks/assign', methods=['POST'])

def assign_task():
    data = request.json
    emp_id = data.get('employee_id')
    title = data.get('title')
    desc = data.get('description', '')
    if not emp_id or not title:
        return jsonify({"error": "Missing employee_id or title"}), 400
    emp = db.get_employee(emp_id)
    from datetime import date
    today = date.today().isoformat()
    today_present = emp.get('last_seen_at', '').startswith(today)
    if not emp or not today_present:
        return jsonify({"error": "Employee not punched today. Punch first."}), 400

    try:
        task = db.assign_task(emp_id, title, desc)
        emp = db.get_employee(emp_id)
        # Send FCM if token
        if emp.get('fcm_token') and fcm_client.enabled:
            fcm_client.send(token=emp['fcm_token'], title=f"New Task: {title}", body=desc or "Check dashboard.")

# Send Discord notification
        discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        if discord_webhook:
            try:
                import requests
                requests.post(discord_webhook, json={"content": f"**New Task Assigned!** Employee {emp_id}: {title}\n{desc or 'Check dashboard.'}"})
            except Exception as e:
                logging.error(f"Discord notify failed: {e}")


        socketio.emit('task_assigned', {'task': task, 'employee': emp})
        return jsonify({'task': task, 'employee': emp})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/iclock/cdata', methods=['GET', 'POST'])
def iclock_cdata():
    raw = request.args.get('txt') or request.get_data(as_text=True) or ''
    logging.info(f"Biometric push: {raw[:200]}...")
    events = adms_parser.parse_essl_payload(raw)
    for event in events:
        pin = event.get('PIN') or event.get('UserID') or event.get('user')
        name = event.get('Name') or event.get('name')
        if pin:
            emp = db.upsert_employee_available(pin, name)
            socketio.emit('status_update', {'employee': emp})
            logging.info(f"✅ {pin}/{name} → Available")
    return "OK"

@socketio.on('connect')
def handle_connect():
    emit('status', {'msg': 'Connected to biometric realtime server'})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=APP_PORT, debug=True)
