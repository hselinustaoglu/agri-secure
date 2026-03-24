FROM timescale/timescaledb-ha:pg16-latest
RUN apt-get update && apt-get install -y postgresql-16-postgis-3 postgresql-16-postgis-3-scripts && rm -rf /var/lib/apt/lists/*
# Development defaults — override with environment variables or secrets in production
ENV POSTGRES_DB=agrisecure
ENV POSTGRES_USER=agrisecure
ENV POSTGRES_PASSWORD=changeme
EXPOSE 5432
