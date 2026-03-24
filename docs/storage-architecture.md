# Storage Architecture — Query-First Design

AgriSecure uses a **query-first** approach: external data is **never stored permanently**.
It is queried on demand and cached temporarily in Redis.

---

## What We Store (Supabase — Free Tier PostgreSQL + PostGIS)

Only **our own data** lives in Supabase:

| Table | Description |
|---|---|
| `farmers` | Farmer profiles, contact info, location |
| `farms` | Farm boundaries, crop types, area |
| `alerts` | Active alerts and notification rules |
| `regions` | Administrative regions (country/admin1/admin2) |
| `data_sources` | External API registry |
| `ingestion_logs` | Audit log of what was queried, when, and with what status |

**Technology**: Supabase free tier — PostgreSQL 15 + PostGIS extension.

**Why Supabase**: Fully managed PostgreSQL with PostGIS, row-level security,
REST and realtime APIs, dashboard UI, and a generous free tier ($0/month).

---

## What We Query On Demand (External APIs → Redis Cache)

External data is **never stored permanently**.  The API fetches it on each
unique request and caches the result in Redis with a TTL.

| Source | Data | Cache TTL |
|---|---|---|
| **Open-Meteo** | 7-day weather forecasts, soil moisture | 1 hour |
| **World Bank RTFP** | Monthly food price estimates | 24 hours |
| **WFP VAM Data Bridges** | Market-level food prices | 24 hours |
| **FAOSTAT** | Crop production, food balance sheets | 24 hours |
| **CHIRPS** | Monthly rainfall file metadata | 24 hours |
| **FEWS NET** | IPC food security phase classifications | 7 days |
| **HeiGIT / HDX** | Risk and accessibility datasets | 7 days |

---

## Caching Strategy (Upstash Redis — Free Tier)

**Technology**: Upstash serverless Redis — pay-per-request, generous free tier ($0/month).

Cache keys follow the pattern:
```
{source}:{query_params...}
```

Examples:
```
open_meteo:-1.286389:36.817223:temperature_2m_max,...
wfp:prices:KEN:wheat:1
fews_net:ipc:KEN:None:None
chirps:2025:03:KEN
heigit:datasets:heigit risk:10:all
```

TTL is configured per source via environment variables:

```env
CACHE_TTL_WEATHER=3600        # 1 hour
CACHE_TTL_PRICES=86400        # 24 hours
CACHE_TTL_FOOD_SECURITY=604800 # 7 days
```

---

## Data Flow

```
Client Request
      │
      ▼
FastAPI /api/v1/external/*
      │
      ├─ Check Redis cache ──── HIT ──► Return cached data (fast)
      │
      └─ MISS
            │
            ▼
      External API (Open-Meteo / WFP / FAOSTAT / FEWS NET / ...)
            │
            ▼
      Cache result in Redis (with TTL)
            │
            ▼
      Return response to client
```

---

## Why Query-First?

| Benefit | Detail |
|---|---|
| **$0/month** | No storage costs for external data |
| **Always current** | Data is fetched fresh (within TTL) on every request |
| **No maintenance** | No ETL pipelines to monitor, no bulk download jobs |
| **No storage limits** | External APIs manage their own storage |
| **Graceful degradation** | If an API is down, the cached value is served |

---

## Phase Progression

As AgriSecure scales beyond the free tiers:

| Phase | Database | Cache | Cost |
|---|---|---|---|
| **MVP (now)** | Supabase free | Upstash free | $0 |
| **Growth** | Supabase Pro | Upstash Pay-as-you-go | ~$25/mo |
| **Scale** | Supabase Enterprise or self-hosted | Redis Cloud | ~$100+/mo |
| **Self-hosted** | PostgreSQL + PostGIS on Hetzner/Civo | Redis on-cluster | ~$20/mo |
