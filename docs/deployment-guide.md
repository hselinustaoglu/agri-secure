# Deployment Guide

## Local Development with Docker Compose

### Prerequisites
- Docker >= 24.0
- Docker Compose >= 2.0

### Steps

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd agri-secure
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env as needed
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

5. **Seed initial data**
   ```bash
   docker-compose exec api python data/seeds/seed.py
   ```

6. **Verify the API**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/docs
   ```

---

## Kubernetes Deployment (MicroK8s)

### Prerequisites
- Ubuntu 20.04+ server
- `sudo` access

### Automated Setup

```bash
chmod +x infra/scripts/setup-microk8s.sh
./infra/scripts/setup-microk8s.sh
```

### Manual Setup

1. **Install MicroK8s**
   ```bash
   sudo snap install microk8s --classic --channel=1.29/stable
   sudo usermod -aG microk8s $USER
   microk8s status --wait-ready
   microk8s enable dns storage ingress
   ```

2. **Apply manifests**
   ```bash
   kubectl apply -f infra/k8s/namespace.yaml
   kubectl apply -f infra/k8s/postgres/
   kubectl apply -f infra/k8s/redis/
   kubectl apply -f infra/k8s/api/
   kubectl apply -f infra/k8s/etl/
   ```

3. **Run migrations**
   ```bash
   kubectl exec -it deploy/agrisecure-api -n agri-secure -- alembic upgrade head
   ```

4. **Seed data**
   ```bash
   kubectl exec -it deploy/agrisecure-api -n agri-secure -- python data/seeds/seed.py
   ```

5. **Verify**
   ```bash
   kubectl get all -n agri-secure
   curl http://agrisecure.local/health
   ```

---

## GitHub Actions

Configure the following repository secrets for automated data ingestion:

| Secret | Description |
|--------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |

Pipelines run on schedule:
- **Daily (6am UTC)**: Open-Meteo weather
- **Weekly (Monday 3am)**: FEWS NET IPC data
- **Monthly (1st 2am)**: World Bank RTFP, WFP, CHIRPS
- **Quarterly (1st of Jan/Apr/Jul/Oct 2am)**: FAOSTAT, HeiGIT Risk, HeiGIT Accessibility
