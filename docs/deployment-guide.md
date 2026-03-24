# Deployment Guide — $0 Stack (Supabase + Upstash)

AgriSecure runs entirely on **free tiers** with no monthly infrastructure cost.

| Component | Service | Cost |
|---|---|---|
| PostgreSQL + PostGIS | Supabase (free tier) | $0 |
| Redis cache | Upstash (free tier) | $0 |
| API / local dev | Docker Compose | $0 |
| ETL automation | GitHub Actions | $0 |
| Frontend (future) | Vercel (free tier) | $0 |
| **Total** | | **$0/month** |

---

## Prerequisites

- **Mac/Linux**: Homebrew, Python 3.11+, Docker Desktop
- **Git** (for cloning the repo)

```bash
# Mac — install Python 3.11
brew install python@3.11

# Verify
python3 --version   # 3.11.x
docker --version    # 24.x+
```

---

## 1. Supabase Setup (Free PostgreSQL + PostGIS)

1. **Sign up** at [supabase.com](https://supabase.com) — free, no credit card.
2. **Create a project** — choose a region close to you.
3. **Enable PostGIS**:
   - Go to **SQL Editor** in your project dashboard.
   - Run: `CREATE EXTENSION IF NOT EXISTS postgis;`
4. **Get credentials** from **Settings → Database**:
   - **Connection string** (Transaction Pooler, port 6543) → your `DATABASE_URL`
   - **Project URL** → `SUPABASE_URL`
   - **API keys** → `SUPABASE_ANON_KEY` and `SUPABASE_SERVICE_KEY`

---

## 2. Upstash Setup (Free Serverless Redis)

1. **Sign up** at [upstash.com](https://upstash.com) — free tier, no credit card.
2. **Create a Redis database** — select the region closest to you.
3. Copy the **Redis connection string** (format: `redis://default:token@host:6379`).

---

## 3. Clone & Configure

```bash
git clone https://github.com/hselinustaoglu/agri-secure.git
cd agri-secure

# Copy and fill in your credentials
cp .env.example .env
# Edit .env — replace placeholders with your Supabase and Upstash values
```

Key variables to set in `.env`:

```env
DATABASE_URL=postgresql://postgres.[your-ref]:[your-password]@aws-0-[region].pooler.supabase.com:6543/postgres
SUPABASE_URL=https://[your-ref].supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
REDIS_URL=redis://default:[your-token]@[your-redis].upstash.io:6379
```

---

## 4. Run Alembic Migrations Against Supabase

```bash
cd services/api
pip install -r requirements.txt
alembic upgrade head
```

This creates all tables in your Supabase project.

---

## 5. Load Seed Data

```bash
python data/seeds/seed.py
```

Seeds reference data: regions, crops, data sources.

---

## 6. Start FastAPI Locally

```bash
# From the repo root
uvicorn services.api.app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for the interactive API docs.

---

## 7. Test External API Queries

```bash
# Weather forecast (queries Open-Meteo, cached 1h in Upstash)
curl "http://localhost:8000/api/v1/external/weather?lat=-1.29&lon=36.82"

# Food prices (queries World Bank + WFP, cached 24h)
curl "http://localhost:8000/api/v1/external/prices?country=KEN&crop=wheat"

# Food security (queries FEWS NET + FAOSTAT, cached 7 days)
curl "http://localhost:8000/api/v1/external/food-security?country=KEN"

# Rainfall metadata (CHIRPS, cached 24h)
curl "http://localhost:8000/api/v1/external/rainfall?country=KEN&year=2025&month=3"

# Risk datasets (HeiGIT via HDX, cached 7 days)
curl "http://localhost:8000/api/v1/external/risk?country=MW"

# Cache stats
curl "http://localhost:8000/api/v1/external/cache/status"
```

---

## 8. Docker Compose (Local Dev with Local Redis)

For offline development, use Docker Compose which spins up a local Redis:

```bash
# Copy and configure .env
cp .env.example .env
# Set DATABASE_URL to your Supabase connection string
# REDIS_URL defaults to redis://redis:6379/0 (local container)

docker-compose up -d

# Run migrations (against Supabase)
docker-compose exec api alembic upgrade head

# Seed data
docker-compose exec api python data/seeds/seed.py
```

To use a fully local PostgreSQL instead of Supabase (offline only):
- Uncomment the `db:` service block in `docker-compose.yml`
- Update `DATABASE_URL` in `.env` to `postgresql://agrisecure:password@db:5432/agrisecure`

---

## 9. GitHub Actions — Cache Warming

Set the following **repository secrets** in GitHub:

| Secret | Description |
|---|---|
| `DATABASE_URL` | Supabase PostgreSQL connection string |
| `REDIS_URL` | Upstash Redis connection string |

Optionally set **repository variables** (not secrets):

| Variable | Default | Description |
|---|---|---|
| `TARGET_COUNTRIES` | `KEN,ETH,NGA` | ISO3 country codes |
| `WEATHER_LOCATIONS` | Kenya/Ethiopia/Nigeria coords | `lat,lon` pairs |

Pipelines run on schedule:

| Schedule | Job | What it warms |
|---|---|---|
| Daily (6am UTC) | `daily-weather` | Open-Meteo weather cache |
| Weekly (Mon 3am) | `weekly-food-security` | FEWS NET IPC cache |
| Monthly (1st 2am) | `monthly-price-snapshot` | World Bank, WFP, CHIRPS cache |
| Quarterly (Jan/Apr/Jul/Oct) | `quarterly-indicators` | FAOSTAT, HeiGIT cache |

You can also trigger any job manually via the **Actions → Run workflow** button.

---

## 10. Optional: MicroK8s on Mac (Kubernetes Learning)

See `infra/k8s/README.md` for step-by-step instructions to deploy AgriSecure on
MicroK8s locally for Kubernetes learning.  This is **not required for production**.

---

## 11. Optional: Vercel Deployment (Frontend — future)

The web dashboard (`apps/web-dashboard/`) will be deployable to Vercel free tier.
Details will be added when the dashboard is implemented.
