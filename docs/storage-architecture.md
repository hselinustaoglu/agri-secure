# Storage Architecture

AgriSecure uses a 3-tier storage design.

## Tier 1: Operational Database (PostgreSQL/PostGIS/TimescaleDB)

**Purpose**: Primary transactional store for all platform data.

**Technology**: TimescaleDB (PostgreSQL + TimescaleDB + PostGIS extensions)

**Hosted on**: Docker container / MicroK8s StatefulSet

**Data**:
- Farmer and farm profiles
- Market prices (time-series)
- Weather data (time-series)
- Food security indicators
- Risk and vulnerability scores
- Alerts and notifications

**Why TimescaleDB**: Optimized for time-series data (market prices, weather, rainfall). Provides automatic partitioning, compression, and continuous aggregates for large datasets.

**Why PostGIS**: Enables spatial queries — finding markets near a farmer, regions within a flood zone, accessibility travel times.

---

## Tier 2: In-Memory Cache (Redis)

**Purpose**: Short-lived cache for frequently accessed or rate-limited API data.

**Technology**: Redis 7

**Use cases**:
- Open-Meteo weather API responses (6-hour TTL)
- API response caching
- Rate limiting for external APIs

---

## Tier 3: Object Storage (S3-compatible)

**Purpose**: Long-term storage for raw files, raster data, and large datasets.

**Technology**: Hetzner Object Storage (S3-compatible)

**Use cases**:
- CHIRPS rainfall TIF files (raw raster downloads)
- FAOSTAT bulk CSV exports
- Model artifacts and processed geospatial datasets
- Backup archives

**Configuration**:
```bash
S3_ENDPOINT=https://fsn1.your-objectstorage.com
S3_BUCKET=agrisecure-data
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
```

---

## Data Flow

```
External APIs (World Bank, WFP, FAOSTAT, FEWS NET, CHIRPS, Open-Meteo, HeiGIT)
       │
       ▼
ETL Pipelines (data/pipelines/)
  ├─ Raw files → Object Storage (S3)
  ├─ Weather API → Redis cache (6h TTL)
  └─ Structured data → PostgreSQL/PostGIS/TimescaleDB
       │
       ▼
FastAPI (services/api/)
  └─ REST endpoints → Client applications
```
