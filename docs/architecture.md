# AgriSecure — System Architecture

## 1. Overview

AgriSecure is a **query-first** food security and agriculture support platform.
External data (weather, prices, food security) is **queried on demand** from free
public APIs and cached temporarily in Redis.  Only our own data (farmers, farms,
alerts) is stored permanently in Supabase.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       EXTERNAL DATA SOURCES (free)                       │
│                                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  FEWS NET│  │  CHIRPS  │  │  WFP VAM │  │ FAOSTAT  │  │Open-Meteo│  │
│  │ (IPC)    │  │(rainfall)│  │ (prices) │  │(crop data│  │(weather) │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │             │             │              │              │         │
│  ┌────┴─────┐  ┌────┴─────┐                                             │
│  │World Bank│  │ HeiGIT   │                                             │
│  │  RTFP    │  │  (HDX)   │                                             │
│  └──────────┘  └──────────┘                                             │
└───────────────────────────┬─────────────────────────────────────────────┘
                             │ Query on demand (HTTPS)
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FastAPI  (services/api/)                               │
│                                                                           │
│  GET /api/v1/external/weather      → OpenMeteoClient                     │
│  GET /api/v1/external/prices       → WorldBankClient + WFPClient         │
│  GET /api/v1/external/food-security→ FEWSNetClient + FAOSTATClient       │
│  GET /api/v1/external/rainfall     → CHIRPSClient                        │
│  GET /api/v1/external/risk         → HeiGITClient                        │
│  GET /api/v1/external/cache/status → RedisCache.stats()                  │
│                                                                           │
│  GET /api/v1/farmers  /farms  /markets  /alerts  /regions  /...          │
└────────────┬──────────────────────────────────────────────┬──────────────┘
             │                                              │
             ▼                                              ▼
┌────────────────────────────┐           ┌─────────────────────────────────┐
│  Supabase (free tier)       │           │  Upstash Redis (free tier)       │
│  PostgreSQL + PostGIS       │           │  Serverless cache                │
│                             │           │                                   │
│  farmers / farms            │           │  open_meteo:lat:lon  (1h TTL)   │
│  alerts / regions           │           │  wfp:prices:KEN:...  (24h TTL)  │
│  data_sources               │           │  fews_net:ipc:KEN:...  (7d TTL) │
│  ingestion_logs             │           │  chirps:2025:03:KEN  (24h TTL)  │
└────────────────────────────┘           └─────────────────────────────────┘
```

---

## 2. $0/Month Cost Breakdown

| Component | Service | Free Tier Limits | Cost |
|---|---|---|---|
| **PostgreSQL + PostGIS** | Supabase | 500 MB DB, 50K MAU | $0 |
| **Redis cache** | Upstash | 10K req/day, 256 MB | $0 |
| **API hosting** | Docker Compose (local) | N/A | $0 |
| **ETL automation** | GitHub Actions | 2,000 min/month | $0 |
| **Frontend** | Vercel (future) | 100 GB bandwidth | $0 |
| **Total** | | | **$0/month** |

---

## 3. Query-First Pattern

All external data follows this flow:

```
1. Client requests /api/v1/external/weather?lat=-1.29&lon=36.82
2. FastAPI checks Redis cache (key: open_meteo:-1.29:36.82:...)
3a. Cache HIT  → Return cached JSON immediately (< 5ms)
3b. Cache MISS → Query Open-Meteo API → Cache result → Return JSON
```

Benefits:
- **Always current**: data is never stale beyond the TTL
- **$0 storage cost**: no raster files, no bulk CSVs stored
- **Graceful degradation**: if an API is down, the last cached value is served

---

## 4. Module Descriptions

### 4.1 External API Clients (`services/api/app/external/`)

Thin async HTTP clients (httpx) for each data source.  Each client:
- Checks Redis cache before making an HTTP request
- Caches the response with a source-specific TTL
- Raises `httpx.HTTPStatusError` on API errors (handled by router)

### 4.2 FastAPI (`services/api/`)
REST API exposing both our own data (farmers, markets, alerts) and proxied
external data queries.  All external endpoints are under `/api/v1/external/`.

### 4.3 Data Pipelines (`data/pipelines/`)
GitHub Actions cache-warming scripts.  They query external APIs proactively
on a schedule and prime the Redis cache so that the first user request is fast.
They also log query metadata to the Supabase `ingestion_logs` table.

### 4.4 Farmer Service (`services/farmer-service/`) — future
Manages farmer registration and profiles.

### 4.5 Advisory Service (`services/advisory-service/`) — future
Generates agronomy advisories based on farmer profile and live weather/price data.

### 4.6 Market Service (`services/market-service/`) — future
Aggregates and serves commodity price data.

### 4.7 Alert Service (`services/alert-service/`) — future
Rule engine that evaluates weather and food-security data against thresholds.

---

## 5. Infrastructure

### Production ($0/month)
- **Supabase**: PostgreSQL + PostGIS (free tier)
- **Upstash**: Serverless Redis (free tier)
- **GitHub Actions**: ETL / cache warming
- **Vercel** (future): Frontend hosting

### Local Development
- **Docker Compose**: FastAPI + local Redis container
- Connect `DATABASE_URL` to Supabase cloud (works offline-first via cache)

### Kubernetes Learning (MicroK8s on Mac)
- See `infra/k8s/README.md` for how to deploy AgriSecure to a local MicroK8s cluster
- This is for learning Kubernetes concepts only — not required for production

---

## 6. Phase Progression

| Phase | Description | Infrastructure |
|---|---|---|
| **MVP** | 2-3 countries, query-first | Supabase free + Upstash free + GitHub Actions |
| **Growth** | 5-10 countries, higher traffic | Supabase Pro + Upstash Pay-per-request |
| **Nonprofit credits** | Apply for AWS/GCP/Azure nonprofit credits | Managed K8s + managed DB |
| **Self-hosted** | Full control, lowest cost at scale | Hetzner/Civo + self-managed PostgreSQL |
