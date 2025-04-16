"""
SQLAlchemy Database Models and Handler for Satellite Product Tracking
"""

from __future__ import annotations


from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database.util.base import Base, BaseMixin


class Constellation(Base, BaseMixin):
    __tablename__ = "constellations"
    name = Column(String(50), primary_key=True)
    description = Column(String(255))
    available_product_types = Column(JSON)
    available_processing_levels = Column(JSON)
    available_sensor_modes = Column(JSON)


class ProductQueryHistory(Base, BaseMixin):
    __tablename__ = "query_history"
    id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    constellation = Column(String(50), ForeignKey("constellations.name"))
    geometry_wkt = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    parameters = Column(JSON)
    constellation_rel = relationship("Constellation")


class DownloadRecord(Base, BaseMixin):
    """
    If they are downloaded.
    """

    __tablename__ = "downloads"
    product_id = Column(String(255), primary_key=True)
    query_id = Column(String(36), ForeignKey("query_history.id"))
    constellation = Column(String(50), ForeignKey("constellations.name"))
    sensor_mode = Column(String(50))
    product_type = Column(String(50))
    processing_level = Column(String(50))
    download_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20))
    acqusition_time = Column(DateTime, nullable=True)
    publication_time = Column(DateTime, nullable=True)
    latency = Column(Float, nullable=True)
    coordinates = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    name = Column(String(255), nullable=True)
    quicklook = Column(String(255), nullable=True)

    file_path = Column(String(255))
    file_size_mb = Column(Float)
    checksum = Column(String(64))
    product_metadata = Column(JSON, name="metadata")

    latency = Column(Float, nullable=True)
    download_time = Column(Float, nullable=True)  # TODO: should probabilitt add some latency
    ingestion_time = Column(DateTime, nullable=True)

    query = relationship("ProductQueryHistory")
    constellation_rel = relationship("Constellation")


class ImageRecord(Base, BaseMixin):
    """
    Images we have.
    """

    __tablename__ = "images"
    id = Column(String(255), primary_key=True)
    constellation = Column(String(50), ForeignKey("constellations.name"))
    acquisition_time = Column(DateTime)
    file_path = Column(String(255))

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    constellation_rel = relationship("Constellation")
    ais_records = relationship("AISRecord", back_populates="image_rel", cascade="all, delete-orphan")


class DetectionRecord(Base, BaseMixin):
    """Detection. Theyre gonna be .json. Donno quite yet.
    TODO: Update this with json.
    """

    __tablename__ = "detections"
    id = Column(String(36), primary_key=True)
    constellation = Column(String(50), ForeignKey("constellations.name"))
    image_id = Column(String(255), ForeignKey("images.id"))
    detection_file = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)

    num_ship_detections = Column(Float)
    num_dark_ship_detections = Column(Float)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    image_rel = relationship("ImageRecord")
    constellation_rel = relationship("Constellation")


class AISRecord(Base, BaseMixin):
    """
    a one to many record of AIS data. AIS data for satellite iamges.
    Donno if this is truly smart,
    but we add it sicne it is easier for the recipent of our deliberable.
    """

    __tablename__ = "ais"

    id = Column(String(36), primary_key=True)
    image_id = Column(String(255), ForeignKey("images.id"), nullable=False)
    mmsi = Column(String(50), nullable=True)
    timestamp = Column(DateTime, nullable=True)
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float, nullable=True)
    heading = Column(Float, nullable=True)
    name = Column(String(50), nullable=True)
    imo = Column(String(50), nullable=True)
    length = Column(String(50), nullable=True)
    type = Column(String(50), nullable=True)

    image_rel = relationship("ImageRecord", back_populates="ais_records")


class ObjectRecord(Base, BaseMixin):
    __tablename__ = "objects"

    id = Column(String, primary_key=True)
    image_id = Column(String, ForeignKey("images.id"))
    obj_class = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    distance_to_shore = Column(Float)
    class_index = Column(String)
    probability = Column(Float)
    probabilities = Column(String)  # JSON-encoded list
    length_min = Column(Float)
    length_max = Column(Float)
    breadth_min = Column(Float)
    breadth_max = Column(Float)
    orientation_min = Column(Float)
    orientation_max = Column(Float)
    speed_min = Column(Float)
    speed_max = Column(Float)
    bbox_width = Column(Float)
    bbox_height = Column(Float)
    bbox_x = Column(Float)
    bbox_y = Column(Float)
    encoded_image = Column(String)
