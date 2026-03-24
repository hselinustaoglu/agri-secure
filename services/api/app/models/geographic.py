import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..database import Base


class Region(Base):
    __tablename__ = "regions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    country_code = Column(String(10), nullable=False)
    admin_level = Column(Integer, nullable=False)
    geometry = Column(Geometry("MULTIPOLYGON", srid=4326), nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("regions.id"), nullable=True)

    parent = relationship(
        "Region",
        remote_side=[id],
        back_populates="children",
        foreign_keys=[parent_id],
    )
    children = relationship(
        "Region",
        back_populates="parent",
        foreign_keys=[parent_id],
    )


class LivelihoodZone(Base):
    __tablename__ = "livelihood_zones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    zone_type = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    geometry = Column(Geometry("MULTIPOLYGON", srid=4326), nullable=True)
