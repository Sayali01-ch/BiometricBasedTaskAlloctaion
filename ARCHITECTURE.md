**Biometric Realtime Architecture Flow (Working)**

```
Biometric Device (ESSL) 
  ↓ POST txt payload
Simulator (device_simulator.py) --> /iclock/cdata (app.py)
  ↓ adms_parser.parse_essl_payload()
db.py upsert_employee_available(id, name) → 'Present' + timestamp (app.db)
  ↓ SocketIO emit 'status_update'
Dashboard (dashboard.html + dashboard.js)
  ↓ io() connect + on('status_update') → upsertRow green fade
  ↕ /api/employees → list_employees() JSON realtime
  ↓ Assign Task /api/tasks/assign → DB task + FCM/Discord notify + emit
Live Events log + Auto refresh 10s

**Status:** Present(green if punched)/Absent(red)
**Notifs:** FCM token + Discord webhook
**Run:** run_backend.ps1 (port 8000, venv)
```

