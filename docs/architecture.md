# AgriSecure — System Architecture

## 1. Overview

AgriSecure is a modular, microservices-based platform that integrates multiple open-source agricultural and food-security tools into a unified system. The diagram below shows the high-level architecture and data flow.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL DATA SOURCES                              │
│                                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────┐ │
│  │ FEWS NET │  │  CHIRPS  │  │ Market APIs  │  │   FAO    │  │   ODK /  │ │
│  │(warnings)│  │(rainfall)│  │(price feeds) │  │(open data│  │KoBoTool. │ │
│  └────┬─────┘  └────┬─────┘  └──────┬───────┘  └────┬─────┘  └────┬─────┘ │
└───────┼─────────────┼───────────────┼───────────────┼──────────────┼───────┘
        │             │               │               │              │
        ▼             ▼               ▼               ▼              ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                         DATA PIPELINES  (data/pipelines/)                     │
│              ETL jobs — ingest, normalise, and load into the database         │
└──────────────────────────────────┬────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     DATABASE LAYER                                           │
│              PostgreSQL + PostGIS (spatial data support)                     │
│                                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌────────────────┐   │
│  │   Farmers   │  │Market Prices │  │Weather/Alert│  │ Vouchers/Input │   │
│  │  (profiles) │  │  (history)   │  │  (timeseries│  │  (subsidy log) │   │
│  └─────────────┘  └──────────────┘  └─────────────┘  └────────────────┘   │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                      BACKEND MICROSERVICES  (services/)                       │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │  farmer-service  │  │ advisory-service │  │  market-service  │          │
│  │  (registration,  │  │ (tip generation, │  │  (price CRUD,    │          │
│  │   profiles)      │  │  scheduling)     │  │   aggregation)   │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                                │
│  │  voucher-service │  │  alert-service   │                                │
│  │  (subsidy track- │  │  (rule engine,   │                                │
│  │   ing, issuance) │  │   notifications) │                                │
│  └──────────────────┘  └──────────────────┘                                │
└──────┬────────────────────────────────────────────────────────┬─────────────┘
       │                                                        │
       ▼                                                        ▼
┌─────────────────────────┐                    ┌───────────────────────────────┐
│   MESSAGING LAYER       │                    │       FRONTEND / APPS         │
│   (apps/sms-gateway/)   │                    │                               │
│                         │                    │  ┌─────────────────────────┐ │
│  Twilio / Africa's      │                    │  │   web-dashboard/        │ │
│  Talking                │                    │  │   (React / Next.js)     │ │
│  ──────────────────     │                    │  │   Analytics, maps,      │ │
│  SMS ◀──▶ Farmer        │                    │  │   agent portal          │ │
│  WhatsApp ◀──▶ Farmer   │                    │  └─────────────────────────┘ │
│                         │                    │                               │
└─────────────────────────┘                    │  ┌─────────────────────────┐ │
                                               │  │   mobile-app/           │ │
                                               │  │   (React Native)        │ │
                                               │  │   Farmer-facing mobile  │ │
                                               │  └─────────────────────────┘ │
                                               └───────────────────────────────┘
```

---

## 2. Module Descriptions

### 2.1 Farmer Service (`services/farmer-service/`)
Manages farmer registration and profiles. Stores personal details, farm location (PostGIS point), crops grown, preferred language, and contact number. Exposes REST endpoints consumed by the web dashboard and mobile app.

### 2.2 Advisory Service (`services/advisory-service/`)
Generates and schedules agronomy advisories based on farmer profile, current weather data, and seasonal calendar. Pushes messages to the SMS gateway for delivery. Integrates with FarmVibes.AI for AI-enhanced recommendations.

### 2.3 Market Service (`services/market-service/`)
Collects, stores, and serves commodity price data. Supports both manual agent entry and automated ingestion from public price APIs. Provides historical trends and alerts for significant price movements.

### 2.4 Voucher Service (`services/voucher-service/`)
Tracks the issuance and redemption of agricultural input subsidies (seeds, fertiliser, tools). Provides audit trail for government programs and NGOs.

### 2.5 Alert Service (`services/alert-service/`)
Implements a rule engine that evaluates incoming weather and food-security data against configurable thresholds. Triggers multi-channel notifications (SMS, WhatsApp, email, dashboard alerts) when thresholds are breached.

### 2.6 SMS Gateway (`apps/sms-gateway/`)
Bridges the backend services and farmer communication channels. Uses Twilio and/or Africa's Talking APIs to send and receive SMS and WhatsApp messages. Handles delivery receipts and inbound message routing.

### 2.7 Web Dashboard (`apps/web-dashboard/`)
React/Next.js application for extension agents, programme managers, and policymakers. Displays interactive maps (Leaflet + PostGIS), farmer statistics, market price charts, food security indicators, and voucher reports.

### 2.8 Mobile App (`apps/mobile-app/`)
React Native application targeting smallholder farmers. Provides registration, advisory message history, market price look-up, and offline-first access to key data.

---

## 3. External Data Source Integrations

| Source | Integration Method | Data Used |
|--------|-------------------|-----------|
| **FEWS NET** | REST/GeoJSON API poll (ETL pipeline) | Food security phase classifications, livelihood zones |
| **CHIRPS** | File download + raster ingestion (ETL pipeline) | Daily/monthly rainfall estimates |
| **Market APIs** | REST API poll or webhook (ETL pipeline) | Commodity prices by region |
| **FAO** | REST API / CSV download | Crop calendars, food consumption reference data |
| **ODK / KoBoToolbox** | REST API + webhook | Field agent survey submissions |

All integrations are implemented as scheduled ETL jobs under `data/pipelines/` and write normalised data to the PostgreSQL database.

---

## 4. Database Layer

- **Engine**: PostgreSQL 15+ with the PostGIS extension for spatial data.
- **Spatial features**: Farm locations stored as `GEOMETRY(Point, 4326)`, enabling proximity queries, choropleth maps, and regional aggregations.
- **Schema per service**: Each microservice owns its schema/tables to maintain loose coupling.
- **Migrations**: Managed via Alembic (Python services) to support versioned schema changes.
- **Seed data**: Reference tables (crop types, administrative regions, languages) are seeded from `data/seeds/`.

---

## 5. Messaging Layer

- **Outbound**: Backend services enqueue messages to the SMS gateway, which dispatches them via Twilio or Africa's Talking.
- **Inbound**: Farmer replies are received by the gateway webhook, parsed, and routed to the advisory service for two-way conversation support.
- **Multi-channel**: SMS (universal), WhatsApp Business API (smartphones), and in-app push notifications (mobile app).
- **Multilingual**: Message templates stored per language; the advisory service selects the correct template based on farmer preference.

---

## 6. Infrastructure

All infrastructure-as-code lives under `infra/`:

- **`infra/terraform/`**: Cloud resource definitions (VPC, compute, managed database, storage buckets) targeting AWS/Azure/GCP.
- **`infra/docker/`**: Docker Compose configuration for local development, bundling all services, the database, and a message broker.

CI/CD is provided by GitHub Actions (`.github/workflows/ci.yml`), running linting and tests on every pull request to `main`.
