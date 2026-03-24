# Kubernetes Manifests — MicroK8s Learning Environment

> **These manifests are for learning Kubernetes on your Mac with MicroK8s.**
> **Production runs on Supabase (free tier) — no Kubernetes required in production.**

## Purpose

This directory contains Kubernetes manifests that demonstrate how AgriSecure could be
deployed to a Kubernetes cluster.  They are intended as a **learning resource** to
practise `kubectl`, understand Deployments/Services/Ingress/CronJobs, and experiment
with MicroK8s locally on your Mac.

They are **not** used in the production $0 stack, which is:

| Component | Production (Free) |
|---|---|
| Database | Supabase (PostgreSQL + PostGIS) |
| Cache | Upstash Redis |
| API hosting | Docker Compose locally or Vercel (future) |
| ETL automation | GitHub Actions |

## Manifest Layout

```
infra/k8s/
├── namespace.yaml          — agri-secure namespace
├── api/
│   ├── configmap.yaml      — API env vars (points to Supabase/Upstash)
│   ├── deployment.yaml     — FastAPI deployment
│   ├── service.yaml        — ClusterIP service
│   └── ingress.yaml        — Nginx Ingress rule
├── redis/
│   ├── deployment.yaml     — Local Redis (for offline MicroK8s dev only)
│   └── service.yaml
├── postgres/               — FOR LOCAL MICROK8S LEARNING ONLY
│   ├── configmap.yaml      — Local Postgres config
│   ├── deployment.yaml     — Local Postgres StatefulSet (not for production)
│   ├── secret.yaml         — Placeholder secret
│   └── service.yaml
└── etl/
    ├── cronjob-daily.yaml
    ├── cronjob-weekly.yaml
    ├── cronjob-monthly.yaml
    └── cronjob-quarterly.yaml
```

> **Note on `postgres/`**: The manifests in `infra/k8s/postgres/` deploy a local
> PostgreSQL instance **for MicroK8s learning only**.  In production, use Supabase.
> Set `DATABASE_URL` in `api/configmap.yaml` (or a Kubernetes Secret) to your
> Supabase connection string instead.

## Quick Start (MicroK8s on Mac)

### Prerequisites

```bash
# Install MicroK8s via Homebrew
brew install ubuntu/microk8s/microk8s
microk8s install
microk8s status --wait-ready
microk8s enable dns storage ingress
alias kubectl='microk8s kubectl'
```

### Deploy

```bash
# 1. Create namespace
kubectl apply -f infra/k8s/namespace.yaml

# 2. (Learning only) Deploy local Postgres and Redis
kubectl apply -f infra/k8s/postgres/
kubectl apply -f infra/k8s/redis/

# 3. Deploy the API
kubectl apply -f infra/k8s/api/

# 4. Deploy ETL CronJobs
kubectl apply -f infra/k8s/etl/

# 5. Check everything is running
kubectl get all -n agri-secure
```

### Run Migrations Against Supabase

```bash
# From your local machine (not inside the cluster)
alembic upgrade head
```

### Useful Commands

```bash
kubectl logs deploy/agrisecure-api -n agri-secure
kubectl exec -it deploy/agrisecure-api -n agri-secure -- bash
kubectl get cronjobs -n agri-secure
kubectl create job --from=cronjob/agrisecure-weather-daily manual-weather -n agri-secure
```

## Cost

Running these manifests on MicroK8s on your Mac costs **$0** — it all runs locally.

For cloud Kubernetes learning, see the options in `docs/architecture.md`.
