FROM timescale/timescaledb-ha:pg16-latest
RUN apt-get update && apt-get install -y postgresql-16-postgis-3 postgresql-16-postgis-3-scripts && rm -rf /var/lib/apt/lists/*
# Set non-sensitive defaults; POSTGRES_PASSWORD must be provided at runtime via
# an environment variable or secret — never hardcode credentials in an image.
ENV POSTGRES_DB=agrisecure
ENV POSTGRES_USER=agrisecure
EXPOSE 5432
