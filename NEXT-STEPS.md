# Next Steps: Production Deployment

**Current:** Dev server running (localhost:8000), scale-ready mods (/metrics, Redis prep).

## Phase 1: Dockerize (Today)
```
docker-compose up  # Nginx + app + Redis + Postgres
```

## Phase 2: Cloud Deploy (Week 1)
1. **AWS/GCP:**
   - EKS (K8s) cluster
   - RDS Postgres (multi-AZ)
   - ElastiCache Redis
   - ALB HTTPS (ACME)
2. Deploy: `kubectl apply -f k8s/`

## Phase 3: Features (Week 2)
1. Rate limiting (`pip install -r requirements-scale.txt`)
2. Celery tasks for FCM/email
3. React frontend

## Phase 4: Monitor (Week 3)
```
helm install prometheus prometheus-community/kube-prometheus-stack
```
Grafana dashboard for P99 latency.

**Immediate Action:** Test /metrics endpoint (live: JSON returned 200 OK).

Run `docker init` now? Or cloud provider choice?
