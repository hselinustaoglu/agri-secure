# Data Sources

AgriSecure queries the following external APIs **on demand** — no bulk downloads,
no local storage.  Results are cached in Redis (Upstash) with source-specific TTLs.

---

## 1. Open-Meteo

- **Description**: Free, open-source weather forecast API — no API key required.
- **Base URL**: `https://api.open-meteo.com/v1`
- **Endpoint**: `GET /forecast?latitude=X&longitude=Y&daily=temperature_2m_max,precipitation_sum,soil_moisture_0_to_7cm`
- **Data**: 7-day daily weather forecasts (temperature, precipitation, soil moisture)
- **Rate limits**: No documented rate limit (fair-use policy)
- **Cache TTL**: 1 hour (`CACHE_TTL_WEATHER=3600`)
- **Client**: `services/api/app/external/open_meteo.py`
- **FastAPI endpoint**: `GET /api/v1/external/weather?lat=X&lon=Y`

---

## 2. World Bank RTFP (Real-Time Food Prices)

- **Description**: Monthly food price estimates by country and commodity (catalog 4483).
- **Base URL**: `https://microdata.worldbank.org/index.php/catalog/4483`
- **Endpoint**: `GET /index.php/api/catalog/4483?format=json`
- **Data**: Food commodity price indices by country/market, monthly frequency
- **Rate limits**: No documented rate limit
- **Cache TTL**: 24 hours (`CACHE_TTL_PRICES=86400`)
- **Client**: `services/api/app/external/world_bank.py`
- **FastAPI endpoint**: `GET /api/v1/external/prices?country=KEN`
- **Reference**: https://microdata.worldbank.org/index.php/catalog/4483

---

## 3. WFP VAM Data Bridges

- **Description**: WFP food market prices via the VAM Data Bridges API v4.
- **Base URL**: `https://api.wfp.org/vam-data-bridges/4.0.0`
- **Endpoint**: `GET /MarketPrices/PriceMonthly?CountryCode=KEN`
- **Data**: Market-level food prices by country and commodity
- **Rate limits**: Requires free API registration at https://api.wfp.org/
- **Cache TTL**: 24 hours (`CACHE_TTL_PRICES=86400`)
- **Client**: `services/api/app/external/wfp.py`
- **FastAPI endpoint**: `GET /api/v1/external/prices?country=KEN&crop=wheat`

---

## 4. FAOSTAT

- **Description**: FAO open data on crop production, food balance sheets, and food security indicators.
- **Base URL**: `https://fenixservices.fao.org/faostat/api/v1`
- **Endpoint**: `GET /en/data/{domain}?area={iso3}&item={code}&year={year}&output_type=json`
- **Key domains**: `QCL` (crop production), `FBS` (food balance sheets), `FS` (food security)
- **Data**: Annual crop production and food security metrics by country
- **Rate limits**: No documented rate limit
- **Cache TTL**: 24 hours (`CACHE_TTL_PRICES=86400`)
- **Client**: `services/api/app/external/faostat.py`
- **FastAPI endpoint**: `GET /api/v1/external/food-security?country=KEN`

---

## 5. FEWS NET

- **Description**: Famine Early Warning Systems Network — IPC food security phase data.
- **Base URL**: `https://fdw.fews.net/api`
- **Endpoint**: `GET /ipcpacket/?country_code=KEN&format=json`
- **Data**: IPC phase classifications (1-5), population affected, period dates
- **Rate limits**: No documented rate limit (public API)
- **Cache TTL**: 7 days (`CACHE_TTL_FOOD_SECURITY=604800`)
- **Client**: `services/api/app/external/fews_net.py`
- **FastAPI endpoint**: `GET /api/v1/external/food-security?country=KEN`

---

## 6. CHIRPS

- **Description**: Climate Hazards Group InfraRed Precipitation with Station data — monthly rainfall.
- **Base URL**: `https://data.chc.ucsb.edu/products/CHIRPS-2.0`
- **Endpoint**: Files at `global_monthly/tifs/chirps-v2.0.{year}.{month:02d}.tif.gz`
- **Data**: Monthly global rainfall rasters (GeoTIFF) — we cache metadata/URLs, not the raw files.
- **Rate limits**: No documented rate limit
- **Cache TTL**: 24 hours (`CACHE_TTL_PRICES=86400`)
- **Client**: `services/api/app/external/chirps.py`
- **FastAPI endpoint**: `GET /api/v1/external/rainfall?country=KEN&year=2025&month=3`

---

## 7. HeiGIT Risk Datasets (via HDX)

- **Description**: Heidelberg Institute for Geoinformation Technology risk indicator datasets.
- **Base URL**: `https://data.humdata.org/api/3`
- **Endpoint**: `GET /action/package_search?q=heigit+risk&rows=10`
- **Data**: Vulnerability and risk indicators for humanitarian planning
- **Rate limits**: No documented rate limit (public CKAN API)
- **Cache TTL**: 7 days (`CACHE_TTL_FOOD_SECURITY=604800`)
- **Client**: `services/api/app/external/heigit.py`
- **FastAPI endpoint**: `GET /api/v1/external/risk?country=MW`
- **Reference**: https://data.humdata.org/organization/heidelberg-institute-for-geoinformation-technology
- **HeiGIT info**: https://heigit.org/five-datasets-to-support-humanitarian-aid-infrastructure-planning-and-climate-action/

---

## 8. HeiGIT Accessibility Datasets (via HDX)

- **Description**: HeiGIT travel-time accessibility to health, market, and education services.
- **Base URL**: `https://data.humdata.org/api/3`
- **Endpoint**: `GET /action/package_search?q=heigit+accessibility&rows=10`
- **Data**: Travel time scores for access to services by admin area
- **Rate limits**: No documented rate limit (public CKAN API)
- **Cache TTL**: 7 days (`CACHE_TTL_FOOD_SECURITY=604800`)
- **Client**: `services/api/app/external/heigit.py`
- **FastAPI endpoint**: `GET /api/v1/external/risk?country=MW`

---

## Summary Table

| Source | Query-on-demand | Cache TTL | API Key Required |
|---|---|---|---|
| Open-Meteo | Yes | 1 hour | No |
| World Bank RTFP | Yes | 24 hours | No |
| WFP VAM Data Bridges | Yes | 24 hours | Free registration |
| FAOSTAT | Yes | 24 hours | No |
| CHIRPS | Yes (metadata only) | 24 hours | No |
| FEWS NET | Yes | 7 days | No |
| HeiGIT Risk (HDX) | Yes | 7 days | No |
| HeiGIT Accessibility (HDX) | Yes | 7 days | No |

---

## Configuration

```env
# Cache TTLs (seconds)
CACHE_TTL_WEATHER=3600
CACHE_TTL_PRICES=86400
CACHE_TTL_FOOD_SECURITY=604800

# External API base URLs
OPEN_METEO_BASE_URL=https://api.open-meteo.com/v1
FAOSTAT_BASE_URL=https://fenixservices.fao.org/faostat/api/v1
WFP_API_BASE_URL=https://api.wfp.org/vam-data-bridges/4.0.0
WORLD_BANK_RTFP_URL=https://microdata.worldbank.org/index.php/catalog/4483
FEWS_NET_BASE_URL=https://fews.net/api
HDX_API_BASE_URL=https://data.humdata.org/api/3

# Target countries and locations for cache warming
TARGET_COUNTRIES=KEN,ETH,NGA
WEATHER_LOCATIONS=-1.286389,36.817223;9.145000,40.489673;9.082000,8.675277
```
