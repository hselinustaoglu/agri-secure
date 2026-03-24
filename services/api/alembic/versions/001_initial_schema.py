"""Initial schema.

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry
import sqlalchemy.dialects.postgresql as pg

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")

    op.create_table(
        "regions",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("country_code", sa.String(10), nullable=False),
        sa.Column("admin_level", sa.Integer, nullable=False),
        sa.Column("geometry", Geometry("MULTIPOLYGON", srid=4326), nullable=True),
        sa.Column(
            "parent_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("regions.id"),
            nullable=True,
        ),
    )

    op.create_table(
        "crops",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("growing_season", sa.String(100), nullable=True),
    )

    op.create_table(
        "farmers",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50), unique=True, nullable=True),
        sa.Column("language", sa.String(10), nullable=True),
        sa.Column("location", Geometry("POINT", srid=4326), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "farms",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "farmer_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("farmers.id"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("area_hectares", sa.Float, nullable=True),
        sa.Column("location", Geometry("POLYGON", srid=4326), nullable=True),
        sa.Column("soil_type", sa.String(100), nullable=True),
    )

    op.create_table(
        "farmer_crops",
        sa.Column(
            "farmer_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("farmers.id"),
            primary_key=True,
        ),
        sa.Column(
            "crop_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("crops.id"),
            primary_key=True,
        ),
        sa.Column("planted_date", sa.Date, nullable=True),
        sa.Column("harvest_date", sa.Date, nullable=True),
        sa.Column("area_hectares", sa.Float, nullable=True),
    )

    op.create_table(
        "markets",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("location", Geometry("POINT", srid=4326), nullable=True),
        sa.Column("country_code", sa.String(10), nullable=False),
        sa.Column("admin_level_1", sa.String(255), nullable=True),
        sa.Column("admin_level_2", sa.String(255), nullable=True),
    )

    op.create_table(
        "market_prices",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "market_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("markets.id"),
            nullable=False,
        ),
        sa.Column(
            "crop_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("crops.id"),
            nullable=False,
        ),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("currency", sa.String(10), nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("price_date", sa.Date, nullable=False),
        sa.Column(
            "source",
            sa.Enum("manual", "world_bank", "wfp", "fao", name="pricesource"),
            nullable=True,
        ),
    )

    op.create_table(
        "price_alerts",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "market_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("markets.id"),
            nullable=True,
        ),
        sa.Column(
            "crop_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("crops.id"),
            nullable=True,
        ),
        sa.Column("alert_type", sa.String(100), nullable=True),
        sa.Column("threshold", sa.Float, nullable=True),
        sa.Column("message", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "weather_data",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("location", Geometry("POINT", srid=4326), nullable=True),
        sa.Column("temperature", sa.Float, nullable=True),
        sa.Column("humidity", sa.Float, nullable=True),
        sa.Column("wind_speed", sa.Float, nullable=True),
        sa.Column("precipitation", sa.Float, nullable=True),
        sa.Column("forecast_date", sa.DateTime, nullable=False),
        sa.Column("source", sa.String(100), nullable=True),
    )

    op.create_table(
        "rainfall_records",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("region_id", pg.UUID(as_uuid=True), nullable=True),
        sa.Column("period_start", sa.Date, nullable=False),
        sa.Column("period_end", sa.Date, nullable=False),
        sa.Column("rainfall_mm", sa.Float, nullable=False),
        sa.Column("anomaly_pct", sa.Float, nullable=True),
        sa.Column(
            "source",
            sa.Enum("chirps", "station", name="rainfallsource"),
            nullable=True,
        ),
    )

    op.create_table(
        "soil_moisture",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("location", Geometry("POINT", srid=4326), nullable=True),
        sa.Column("depth_cm", sa.Integer, nullable=True),
        sa.Column("moisture_pct", sa.Float, nullable=True),
        sa.Column("measurement_date", sa.DateTime, nullable=False),
        sa.Column("source", sa.String(100), nullable=True),
    )

    op.create_table(
        "risk_assessments",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("admin_area_id", pg.UUID(as_uuid=True), nullable=True),
        sa.Column("indicator_type", sa.String(100), nullable=True),
        sa.Column("value", sa.Float, nullable=True),
        sa.Column("score", sa.Float, nullable=True),
        sa.Column("assessment_date", sa.Date, nullable=False),
        sa.Column("source", sa.String(100), nullable=True),
    )

    op.create_table(
        "vulnerability_indicators",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("admin_area_id", pg.UUID(as_uuid=True), nullable=True),
        sa.Column("demographic_score", sa.Float, nullable=True),
        sa.Column("environmental_score", sa.Float, nullable=True),
        sa.Column("infrastructure_score", sa.Float, nullable=True),
        sa.Column("overall_score", sa.Float, nullable=True),
    )

    op.create_table(
        "flood_exposures",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("admin_area_id", pg.UUID(as_uuid=True), nullable=True),
        sa.Column("exposure_level", sa.String(50), nullable=True),
        sa.Column("affected_population", sa.Integer, nullable=True),
        sa.Column("area_km2", sa.Float, nullable=True),
        sa.Column("assessment_date", sa.Date, nullable=False),
    )

    op.create_table(
        "accessibility_scores",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("admin_area_id", pg.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "service_type",
            sa.Enum("health", "education", "market", name="servicetype"),
            nullable=False,
        ),
        sa.Column("travel_time_minutes", sa.Float, nullable=True),
        sa.Column("population_covered", sa.Integer, nullable=True),
    )

    op.create_table(
        "alerts",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "alert_type",
            sa.Enum("drought", "flood", "pest", "price_spike", name="alerttype"),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.Enum("low", "medium", "high", "critical", name="alertseverity"),
            nullable=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("location", Geometry("POINT", srid=4326), nullable=True),
        sa.Column("affected_area", Geometry("MULTIPOLYGON", srid=4326), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "alert_rules",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("rule_name", sa.String(255), nullable=False),
        sa.Column("condition_json", sa.Text, nullable=True),
        sa.Column(
            "action",
            sa.Enum("sms", "email", "whatsapp", name="alertaction"),
            nullable=False,
        ),
        sa.Column("active", sa.Boolean, nullable=True),
    )

    op.create_table(
        "alert_notifications",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "alert_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("alerts.id"),
            nullable=False,
        ),
        sa.Column(
            "farmer_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("farmers.id"),
            nullable=True,
        ),
        sa.Column("channel", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("sent_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "data_sources",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("url", sa.String(1000), nullable=True),
        sa.Column("source_type", sa.String(50), nullable=True),
        sa.Column("refresh_interval", sa.Integer, nullable=True),
        sa.Column("last_sync", sa.DateTime, nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("config_json", sa.Text, nullable=True),
    )

    op.create_table(
        "ingestion_logs",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "data_source_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("data_sources.id"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        sa.Column(
            "status",
            sa.Enum("success", "failed", "partial", name="ingestionstatus"),
            nullable=False,
        ),
        sa.Column("rows_processed", sa.Integer, nullable=True),
        sa.Column("rows_failed", sa.Integer, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
    )

    op.create_table(
        "sync_schedules",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "data_source_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("data_sources.id"),
            nullable=False,
        ),
        sa.Column("cron_expression", sa.String(100), nullable=False),
        sa.Column("next_run", sa.DateTime, nullable=True),
        sa.Column("last_success", sa.DateTime, nullable=True),
        sa.Column("enabled", sa.Boolean, nullable=True),
    )

    op.create_table(
        "livelihood_zones",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("zone_type", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("geometry", Geometry("MULTIPOLYGON", srid=4326), nullable=True),
    )

    op.create_table(
        "food_security_indicators",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "region_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("regions.id"),
            nullable=True,
        ),
        sa.Column(
            "indicator_type",
            sa.Enum(
                "ipc_phase", "fcs", "hdds", "rcsi", name="foodsecurityindicatortype"
            ),
            nullable=False,
        ),
        sa.Column("value", sa.Float, nullable=True),
        sa.Column("classification", sa.String(100), nullable=True),
        sa.Column("period_start", sa.Date, nullable=False),
        sa.Column("period_end", sa.Date, nullable=False),
        sa.Column("source", sa.String(100), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("food_security_indicators")
    op.drop_table("livelihood_zones")
    op.drop_table("sync_schedules")
    op.drop_table("ingestion_logs")
    op.drop_table("data_sources")
    op.drop_table("alert_notifications")
    op.drop_table("alert_rules")
    op.drop_table("alerts")
    op.drop_table("accessibility_scores")
    op.drop_table("flood_exposures")
    op.drop_table("vulnerability_indicators")
    op.drop_table("risk_assessments")
    op.drop_table("soil_moisture")
    op.drop_table("rainfall_records")
    op.drop_table("weather_data")
    op.drop_table("price_alerts")
    op.drop_table("market_prices")
    op.drop_table("markets")
    op.drop_table("farmer_crops")
    op.drop_table("farms")
    op.drop_table("farmers")
    op.drop_table("crops")
    op.drop_table("regions")
    op.execute("DROP TYPE IF EXISTS foodsecurityindicatortype")
    op.execute("DROP TYPE IF EXISTS ingestionstatus")
    op.execute("DROP TYPE IF EXISTS alertaction")
    op.execute("DROP TYPE IF EXISTS alertseverity")
    op.execute("DROP TYPE IF EXISTS alerttype")
    op.execute("DROP TYPE IF EXISTS servicetype")
    op.execute("DROP TYPE IF EXISTS rainfallsource")
    op.execute("DROP TYPE IF EXISTS pricesource")
