from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database import Base


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    units = relationship("Unit", back_populates="upload", cascade="all, delete-orphan")


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)

    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)

    developer_name = Column(String, nullable=True)
    project_name = Column(String, nullable=True)
    location = Column(String, nullable=True)
    district = Column(String, nullable=True)
    stage = Column(String, nullable=True)
    unit_type = Column(String, nullable=True)

    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)

    area_m2 = Column(Float, nullable=True)
    price_total = Column(Float, nullable=True)
    price_per_m2 = Column(Float, nullable=True)

    delivery_date = Column(String, nullable=True)
    finishing_status = Column(String, nullable=True)
    building = Column(String, nullable=True)
    floor_number = Column(String, nullable=True)
    unit_code = Column(String, nullable=True)
    source_file = Column(String, nullable=True)

    raw_data = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    upload = relationship("Upload", back_populates="units")