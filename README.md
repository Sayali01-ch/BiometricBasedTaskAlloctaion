# 🚀 Biometric Realtime Attendance & Task Allocation System
[![GitHub stars](https://img.shields.io/github/stars/Sayali01-ch/BiometricBasedTaskAlloctaion)](https://github.com/Sayali01-ch/BiometricBasedTaskAlloctaion) [![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)

**Industry-scalable** end-to-end solution:
- **Biometric punches** → **Live dashboard** (Socket.IO realtime)
- **Task assignment** to available employees → **FCM push notifications**
- **eSSL ADMS** ready (`/iclock/cdata`)
- **Docker/K8s** production path documented

Live demo repo: https://github.com/Sayali01-ch/BiometricBasedTaskAlloctaion

## 🎯 Features
| Feature | Status |
|---------|--------|
| Realtime attendance dashboard | ✅ |
| eSSL biometric integration | ✅ |
| Employee task assignment | ✅ |
| FCM mobile notifications | ✅ |
| Discord webhooks | ✅ |
| Device simulator | ✅ |
| Metrics endpoint (`/metrics`) | ✅ |
| Scale-ready (Redis/Postgres) | 📈 Docs |

## 📁 Project Structure
```
BiometricRealtimeTask/
├── backend/                 # Flask + Socket.IO server
│   ├── app.py              # Main API + SocketIO
│   ├── db.py               # SQLite ORM (Postgres ready)
│   ├── fcm.py              # Firebase Cloud Messaging
│   ├── adms_parser.py      # eSSL ADMS payload parser
│   ├── requirements.txt    # Base deps
│   └── requirements-scale.txt # Redis/Celery production
├── scripts/
│   └── device_simulator.py # Simulate punches
├── backend/templates/      # HTML dashboard
├── backend/static/         # dashboard.js
├── run_backend.ps1         # Windows runner
├── SCALABILITY.md          # K8s path
├── ARCHITECTURE.md         # Flow diagram
└── NEXT-STEPS.md           # Deploy plan
```

## 🚀 Quick Start (Windows/Mac/Linux)

### 1. Clone & Backend
```bash
git clone https://github.com/Sayali01-ch/BiometricBasedTaskAlloctaion.git
cd BiometricBasedTaskAlloctaion/backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
pip install -r requirements-scale.txt  # Scale-ready
python app.py
```
**Port:** `http://localhost:5000/dashboard` (change via `PORT=8000`)

### 2. Test Punch (Simulator)
```bash
# New terminal (venv active)
python ../scripts/device_simulator.py --pin 101 --name "Asha Patel" --times 3
```
✅ Dashboard: Employee row **turns green instantly**!

### 3. Assign Task (Live)
- Dashboard → Select green employee → "Assign Task"
- **FCM push** sent (if token configured)

## 🔌 Connect Real Biometric Device (eSSL K40/X200)

1. **Find server IP:**
   ```bash
   # Windows
   ipconfig | findstr "IPv4"
   # Mac/Linux
   ip route | grep default | awk '{print $3}'
   ```
   Example: `192.168.1.105`

2. **Device Menu:** `Menu > Comm > ADMS/Cloud`
   ```
   Server Address: 192.168.1.105
   Server Port: 5000
   Path: /iclock/cdata (auto)
   ```

3. **Windows Firewall:**
   ```powershell
   netsh advfirewall firewall add rule name="BiometricRealtime" dir=in action=allow protocol=TCP localport=5000
   ```

4. **Punch card** → Instant dashboard update + log: `✅ 101/Asha → Available`

**Supported payloads:** Tab/KV, CSV (adms_parser.py tolerant)

## 📱 FCM Notifications Setup
1. [Firebase Console](https://console.firebase.google.com) → Project → Service Account → JSON
2. Save as `backend/credentials/firebase-credentials.json`
3. Env var:
   ```powershell
   $env:FCM_SERVICE_ACCOUNT_JSON="C:\full\path\firebase-credentials.json"
   ```
4. **Employee app** POST FCM token: `/api/employees/101/fcm-token`
5. Task assign → Instant phone notification!

**Discord too:** `$env:DISCORD_WEBHOOK_URL="https://discord.com/..."`

## 🧪 API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/dashboard` | GET | Realtime UI |
| `/iclock/cdata` | POST/GET | eSSL punches |
| `/api/employees` | GET | Employee list |
| `/api/tasks/assign` | POST | Assign + notify |
| `/metrics` | GET | Prometheus ready |
| `/status` | GET | Health |

## 🏗️ Production Scale Path (SCALABILITY.md)
```
SQLite → Postgres (RDS)
Flask → FastAPI + Celery
SocketIO → Redis pub/sub (multi-instance)
Deploy: Docker → K8s EKS
Monitor: Prometheus + Grafana
```
**10k concurrent users ready** (Week 1 Docker wins).

## 🔧 Troubleshooting
| Issue | Fix |
|-------|-----|
| No punches | Check IP/port, firewall |
| FCM fails | Verify JSON path/env |
| Dashboard stuck | Hard refresh, check console |
| Scale deps | `pip install -r requirements-scale.txt` |

## 📖 More Docs
- [ARCHITECTURE.md](ARCHITECTURE.md) - Flow diagram
- [SCALABILITY.md](SCALABILITY.md) - Industry scale
- [NEXT-STEPS.md](NEXT-STEPS.md) - Deploy plan

## 🤝 Contributing
```
git checkout -b feature/xyz
git commit -m "feat: add xyz"
git push origin feature/xyz
gh pr create --fill
```

**Stars/forks welcome!** Questions? Open issue.

© 2026 Sayali01-ch | [License](LICENSE)
