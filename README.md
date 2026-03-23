# 🌾 AgriSecure

<!-- Logo placeholder: replace with actual logo image -->
<!-- ![AgriSecure Logo](docs/assets/logo.png) -->

> **Unified open-source Food Security & Agriculture Support Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://github.com/hselinustaoglu/agri-secure/actions/workflows/ci.yml/badge.svg)](https://github.com/hselinustaoglu/agri-secure/actions/workflows/ci.yml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## 🚩 Problem Statement

Food insecurity affects hundreds of millions of people worldwide, yet the tools that exist to address it — climate data platforms, farmer advisory systems, market price trackers, early warning networks — operate in **isolated silos**. Extension agents juggle multiple apps. Farmers receive inconsistent or delayed guidance. Decision-makers lack a unified view of conditions on the ground.

Key gaps:
- **Fragmented tools**: FEWS NET, CHIRPS, FarmStack, ODK, and others are not integrated.
- **Last-mile communication**: Smallholder farmers often rely on basic phones — SMS and WhatsApp are critical but under-utilised.
- **Data silos**: Market prices, weather anomalies, and voucher distribution data are rarely connected.
- **Limited actionability**: Dashboards exist, but triggering alerts and advisories remains manual.

---

## 💡 Solution Overview

AgriSecure is a **unified, open-source platform** that integrates existing best-in-class open-source tools into a single cohesive system. It provides:

| Module | Description |
|--------|-------------|
| 🌱 **Farmer Advisory** | Personalised SMS/WhatsApp agronomy tips (weather, pest, planting) |
| 📊 **Market Price Intelligence** | Real-time and historical commodity price tracking and alerts |
| ⚠️ **Early Warning System** | Climate and food-security alerts powered by FEWS NET & CHIRPS |
| 🗺️ **Food Security Dashboard** | Interactive maps and analytics for extension agents and policymakers |
| 🎟️ **Input/Subsidy Voucher Tracker** | End-to-end tracking of agricultural input subsidies |

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React / Next.js (web dashboard), React Native (mobile app) |
| **Backend** | Python FastAPI (microservices) |
| **Database** | PostgreSQL + PostGIS (spatial queries) |
| **Messaging** | Twilio / Africa's Talking (SMS & WhatsApp) |
| **Maps** | Leaflet, Google Earth Engine |
| **ML / AI** | FarmVibes.AI |
| **Data Sources** | FEWS NET, CHIRPS, FAO |
| **Hosting** | AWS / Azure / GCP |
| **CI/CD** | GitHub Actions |

---

## 🔗 Open-Source Integrations

| Tool | Purpose |
|------|---------|
| [FEWS NET](https://fews.net/) | Food security early warning data |
| [CHIRPS](https://www.chc.ucsb.edu/data/chirps) | Rainfall estimates for climate monitoring |
| [FarmStack](https://farmstack.co/) | Federated agricultural data exchange |
| [FarmVibes.AI](https://github.com/microsoft/farmvibes-ai) | AI/ML models for agriculture |
| [ODK / KoBoToolbox](https://www.kobotoolbox.org/) | Mobile data collection for field agents |
| [farmOS](https://farmos.org/) | Farm record management |

---

## 📁 Directory Structure

```
agri-secure/
├── apps/
│   ├── web-dashboard/       # React/Next.js admin & analytics dashboard
│   ├── mobile-app/          # React Native farmer-facing mobile app
│   └── sms-gateway/         # Twilio/WhatsApp integration service
├── services/
│   ├── farmer-service/      # Farmer registration & profiles
│   ├── advisory-service/    # Weather, pest, planting tip advisories
│   ├── market-service/      # Price collection & display
│   ├── voucher-service/     # Input subsidy management
│   └── alert-service/       # Early warning system
├── data/
│   ├── seeds/               # Reference data (crops, regions, languages)
│   └── pipelines/           # ETL pipelines for FEWS NET, CHIRPS, etc.
├── infra/
│   ├── terraform/           # Infrastructure as code
│   └── docker/              # Docker and docker-compose configs
├── docs/
│   ├── architecture.md      # High-level architecture overview
│   └── api-design.md        # API design guidelines
├── .github/
│   ├── workflows/ci.yml     # GitHub Actions CI workflow
│   └── CODEOWNERS
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

---

## 🚀 Getting Started

> **Note:** Full setup instructions will be added as each service is implemented. The following is a placeholder workflow.

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 15+ with PostGIS extension

### Clone the repository

```bash
git clone https://github.com/hselinustaoglu/agri-secure.git
cd agri-secure
```

### Run with Docker Compose (coming soon)

```bash
cd infra/docker
docker-compose up
```

### Running a service locally (example)

```bash
cd services/farmer-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to fork, branch, and submit pull requests.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) — © 2026 hselinustaoglu.
