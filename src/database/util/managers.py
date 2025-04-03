from __future__ import annotations
from typing import Dict, Any, Optional, List, Union
from uuid import uuid4
from database.util.tables import Constellation, ProductQueryHistory, DownloadRecord, ImageRecord, DetectionRecord, AISRecord
from datetime import datetime, timezone


class AISManager:
    def __init__(self, session_factory, db_handler):
        self.session_factory = session_factory
        self.db_handler = db_handler

    def insert_ais_records(self, image_id: str, ais_data: Union[List[Dict[str, Any]], list[Dict[str, Any]]]):
        """
        Insert AIS records linked to a given image.

        Args:
            image_id (str): ID of the ImageRecord
            ais_data (list): List of dicts with AIS data fields
        """
        if not ais_data:
            return

        with self.db_handler.session_scope() as session:
            records = [
                AISRecord(
                    id=str(uuid4()),
                    image_id=image_id,
                    mmsi=entry.get("mmsi"),
                    timestamp=entry.get("timestamp"),
                    latitude=entry.get("latitude"),
                    longitude=entry.get("longitude"),
                    speed=entry.get("speed"),
                    heading=entry.get("heading"),
                    name=entry.get("name"),
                    imo=entry.get("imo"),
                    length=entry.get("length"),
                    type=entry.get("type"),
                )
                for entry in ais_data
            ]
            session.add_all(records)


class ConstellationManager:
    def __init__(self, session_factory, db_handler):
        self.db_handler = db_handler
        self.session_factory = session_factory

    def _populate_constellations(self, satellite_config: dict):
        with self.db_handler.session_scope() as session:
            for name, config in satellite_config.items():
                if not session.query(Constellation).filter_by(name=name).first():
                    session.add(
                        Constellation(
                            name=name,
                            description=f"{name} satellite constellation",
                            available_product_types=config.get("product_types", []),
                            available_processing_levels=config.get("processing_levels", []),
                            available_sensor_modes=config.get("sensor_modes", []),
                        )
                    )


class QueryManager:
    def __init__(self, session_factory, db_handler):
        self.db_handler = db_handler
        self.session_factory = session_factory

    def record_query(self, query_data: Dict[str, Any]) -> str:
        with self.db_handler.session_scope() as session:
            query_id = str(uuid4())
            session.add(
                ProductQueryHistory(
                    id=query_id,
                    constellation=query_data["constellation"],
                    geometry_wkt=query_data["geometry_wkt"],
                    start_date=query_data["start_date"],
                    end_date=query_data["end_date"],
                    parameters=query_data.get("parameters", {}),
                )
            )
            return query_id


class DownloadManager:
    def __init__(self, session_factory, db_handler):
        self.db_handler = db_handler
        self.session_factory = session_factory

    def record_download(self, product_data: Dict[str, Any], status: Optional[str] = None):
        with self.db_handler.session_scope() as session:
            session.add(
                DownloadRecord(
                    product_id=product_data.get("product_id"),
                    query_id=product_data.get("query_id"),
                    constellation=product_data.get("constellation"),
                    sensor_mode=product_data.get("sensor_mode"),
                    product_type=product_data.get("product_type"),
                    processing_level=product_data.get("processing_level"),
                    status=status or product_data.get("status", "unknown"),
                    acqusition_time=product_data.get("acqusition_time"),
                    publication_time=product_data.get("publication_time"),
                    latency=product_data.get("latency"),
                    coordinates=str(product_data.get("coordinates")),
                    latitude=product_data.get("latitude"),
                    longitude=product_data.get("longitude"),
                    name=product_data.get("name"),
                    quicklook=product_data.get("quicklook"),
                    file_path=str(product_data.get("file_path")),
                    file_size_mb=product_data.get("file_size_mb"),
                    checksum=product_data.get("checksum"),
                    product_metadata=product_data.get("metadata"),
                    ingestion_time=product_data.get("ingestion_time", datetime.now(timezone.utc)),
                )
            )


class DetectionManager:
    def __init__(self, session_factory, db_handler):
        self.db_handler = db_handler
        self.session_factory = session_factory

    def record_detection(self, detection: Dict[str, Any]):
        with self.db_handler.session_scope() as session:
            session.add(
                DetectionRecord(
                    id=str(uuid4()),
                    constellation=detection["constellation"],
                    image_id=detection["image_id"],
                    detection_file=str(detection["detection_file"]),
                    num_ship_detections=detection.get("num_ship_detections"),
                    num_dark_ship_detections=detection.get("num_dark_ship_detections"),
                    latitude=detection.get("latitude"),
                    longitude=detection.get("longitude"),
                )
            )


class ImageManager:
    def __init__(self, session_factory, db_handler):
        self.db_handler = db_handler
        self.session_factory = session_factory

    def register_image(self, image_data: Dict[str, Any]):
        with self.db_handler.session_scope() as session:
            if not session.query(ImageRecord).filter_by(id=image_data["id"]).first():
                session.add(
                    ImageRecord(
                        id=image_data["id"],
                        constellation=image_data["constellation"],
                        acquisition_time=image_data.get("acquisition_time"),
                        file_path=str(image_data["file_path"]),
                        latitude=image_data.get("latitude"),
                        longitude=image_data.get("longitude"),
                    )
                )
