"""Seed script to load initial data into the database."""

import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SEEDS_DIR = Path(__file__).parent


def get_session() -> Any:
    db_url = os.environ.get(
        "DATABASE_URL", "postgresql://agrisecure:changeme@localhost:5432/agrisecure"
    )
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()


def load_crops(session: Any) -> None:
    with open(SEEDS_DIR / "crops.json") as f:
        crops: List[Dict[str, Any]] = json.load(f)
    for crop in crops:
        existing = session.execute(
            text("SELECT id FROM crops WHERE name = :name"), {"name": crop["name"]}
        ).fetchone()
        if not existing:
            session.execute(
                text(
                    "INSERT INTO crops (id, name, category, growing_season) "
                    "VALUES (:id, :name, :category, :growing_season)"
                ),
                {"id": str(uuid.uuid4()), **crop},
            )
    session.commit()
    logger.info("Crops seeded.")


def load_regions(session: Any) -> None:
    with open(SEEDS_DIR / "regions.json") as f:
        regions: List[Dict[str, Any]] = json.load(f)

    country_ids: Dict[str, str] = {}

    for region in regions:
        if region.get("admin_level") == 0:
            existing = session.execute(
                text(
                    "SELECT id FROM regions WHERE name = :name AND country_code = :cc"
                ),
                {"name": region["name"], "cc": region["country_code"]},
            ).fetchone()
            if existing:
                country_ids[region["name"]] = str(existing[0])
            else:
                region_id = str(uuid.uuid4())
                session.execute(
                    text(
                        "INSERT INTO regions (id, name, country_code, admin_level) "
                        "VALUES (:id, :name, :cc, :level)"
                    ),
                    {
                        "id": region_id,
                        "name": region["name"],
                        "cc": region["country_code"],
                        "level": 0,
                    },
                )
                country_ids[region["name"]] = region_id
    session.commit()

    for region in regions:
        if region.get("admin_level", 0) > 0:
            parent_name = region.get("parent_country")
            parent_id = country_ids.get(parent_name) if parent_name else None
            existing = session.execute(
                text(
                    "SELECT id FROM regions WHERE name = :name AND country_code = :cc"
                ),
                {"name": region["name"], "cc": region["country_code"]},
            ).fetchone()
            if not existing:
                session.execute(
                    text(
                        "INSERT INTO regions (id, name, country_code, admin_level, parent_id) "
                        "VALUES (:id, :name, :cc, :level, :parent_id)"
                    ),
                    {
                        "id": str(uuid.uuid4()),
                        "name": region["name"],
                        "cc": region["country_code"],
                        "level": region.get("admin_level", 1),
                        "parent_id": parent_id,
                    },
                )
    session.commit()
    logger.info("Regions seeded.")


def load_data_sources(session: Any) -> None:
    with open(SEEDS_DIR / "data_sources.json") as f:
        sources: List[Dict[str, Any]] = json.load(f)
    for source in sources:
        existing = session.execute(
            text("SELECT id FROM data_sources WHERE name = :name"),
            {"name": source["name"]},
        ).fetchone()
        if not existing:
            config = source.get("config_json")
            session.execute(
                text(
                    "INSERT INTO data_sources "
                    "(id, name, url, source_type, refresh_interval, status, config_json) "
                    "VALUES (:id, :name, :url, :source_type, :refresh_interval, :status, :config_json)"
                ),
                {
                    "id": str(uuid.uuid4()),
                    "name": source["name"],
                    "url": source.get("url"),
                    "source_type": source.get("source_type"),
                    "refresh_interval": source.get("refresh_interval"),
                    "status": source.get("status", "active"),
                    "config_json": json.dumps(config) if config else None,
                },
            )
    session.commit()
    logger.info("Data sources seeded.")


def main() -> None:
    session = get_session()
    try:
        load_crops(session)
        load_regions(session)
        load_data_sources(session)
        logger.info("All seed data loaded successfully.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
