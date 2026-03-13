# Biometric Realtime Attendance + Task Allocation

End-to-end reference implementation for your manager’s requirement:

- Biometric device (eSSL ADMS push) hits backend at `GET/POST /iclock/cdata`
- Backend marks employee **Available** and pushes live update to dashboard via Socket.IO
- Manager assigns task to an available employee
- Backend sends **phone notification** via Firebase Cloud Messaging (FCM) (when configured)

## Project structure

- `backend/` Flask + Socket.IO server (dashboard + APIs)
- `scripts/` helper scripts (device simulator)

## Prerequisites

- Python 3.10+ recommended

## Setup (Windows PowerShell)

```powershell
cd "C:\Users\Sanskruti Chopade\BiometricRealtimeTask\backend"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open dashboard:

- `http://localhost:8000`

## Simulate a biometric scan (device push)

In a second terminal:

```powershell
cd "C:\Users\Sanskruti Chopade\BiometricRealtimeTask\scripts"
..\backend\.venv\Scripts\python.exe device_simulator.py --pin 101 --name "Asha"
```

You should see the employee row turn **green** (Available) instantly.

## Configure eSSL X2008 ADMS

Set ADMS/Cloud server to your backend:

- **Server Address**: your PC’s LAN IP (e.g. `192.168.1.50`)
- **Server Port**: `8000`
- Device will push to `/iclock/cdata` (standard eSSL path)

Make sure Windows Firewall allows inbound TCP `8000`.

## FCM (phone notifications)

This project supports FCM via **firebase-admin**.

1. Create a Firebase project and service account JSON.
2. Set env var pointing to the service account JSON:

```powershell
$env:FCM_SERVICE_ACCOUNT_JSON="C:\path\to\service-account.json"
```

3. The mobile app must POST its FCM token to:

- `POST /api/employees/<employee_id>/fcm-token`

When a manager assigns a task, the backend sends an FCM push if a token exists.

## Notes

- Uses SQLite for demo (`backend/app.db`). Easy to swap to Postgres/MySQL later.
- Real device payload formats vary; `/iclock/cdata` handler is tolerant and logs raw lines.

