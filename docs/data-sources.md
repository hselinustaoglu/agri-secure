# Data Sources

AgriSecure ingests data from the following external sources.

## 1. World Bank RTFP
- **Description**: Real-Time Food Prices monthly estimates
- **URL**: https://microdata.worldbank.org/index.php/api/catalog/4483
- **Frequency**: Monthly
- **Data**: Food commodity prices by country/market
- **Pipeline**: `data/pipelines/world_bank_rtfp.py`

## 2. WFP HungerMap
- **Description**: WFP food market prices
- **URL**: https://api.hungermapdata.org/api/v2/country/all/marketprice
- **Frequency**: Monthly
- **Data**: Market-level food prices
- **Pipeline**: `data/pipelines/wfp_prices.py`

## 3. FAOSTAT
- **Description**: FAO crop production statistics
- **URL**: https://fenixservices.fao.org/faostat/api/v1/en/data/QCL
- **Frequency**: Quarterly
- **Data**: Annual crop production by country
- **Pipeline**: `data/pipelines/faostat.py`

## 4. FEWS NET
- **Description**: Famine Early Warning Systems Network IPC phases
- **URL**: https://fdw.fews.net/api/ipcpacket/
- **Frequency**: Weekly
- **Data**: IPC food security phase classifications
- **Pipeline**: `data/pipelines/fews_net.py`

## 5. CHIRPS
- **Description**: Climate Hazards Group InfraRed Precipitation with Station data
- **URL**: https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs/
- **Frequency**: Monthly
- **Data**: Monthly rainfall estimates (TIF raster files)
- **Pipeline**: `data/pipelines/chirps.py`

## 6. Open-Meteo
- **Description**: Open-source weather forecast API
- **URL**: https://api.open-meteo.com/v1/forecast
- **Frequency**: Daily (6h Redis cache)
- **Data**: 7-day weather forecasts for configured locations
- **Pipeline**: `data/pipelines/open_meteo.py`

## 7. HeiGIT Risk
- **Description**: Heidelberg Institute for Geoinformation Technology risk indicators
- **URL**: https://data.humdata.org/api/3/action/package_search?q=heigit+risk
- **Frequency**: Quarterly
- **Data**: Vulnerability and risk indicators
- **Pipeline**: `data/pipelines/heigit_risk.py`

## 8. HeiGIT Accessibility
- **Description**: HeiGIT accessibility to services indicators
- **URL**: https://data.humdata.org/api/3/action/package_search?q=heigit+accessibility
- **Frequency**: Quarterly
- **Data**: Travel time to health, education, and market services
- **Pipeline**: `data/pipelines/heigit_accessibility.py`

## Configuration

Set the following environment variables to control ETL behavior:

```bash
TARGET_COUNTRIES=KEN,ETH,NGA
WEATHER_LOCATIONS=-1.286389,36.817223;9.145000,40.489673;9.082000,8.675277
DATABASE_URL=postgresql://agrisecure:changeme@localhost:5432/agrisecure
REDIS_URL=redis://localhost:6379/0
```
