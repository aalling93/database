from __future__ import annotations
from typing import Dict, Any
from uuid import uuid4

from database.util.tables import Constellation, ProductQueryHistory, DownloadRecord, ImageRecord, DetectionRecord, AISRecord


class AISManager:
    def __init__(self, session_factory, db_handler):
        self.session_factory = session_factory
        self.db_handler = db_handler

    def insert_ais_records(self, image_id: str, ais_data: list[dict[str, Any]]):
        """
        Insert AIS records linked to a given image.

        Args:
            image_id (str): ImageRecord ID
            ais_data (list[dict]): Each dict is one AIS row
        """
        if not ais_data:
            return  # Nothing to insert

        with self.db_handler.session_scope() as session:
            records = [AISRecord(id=str(uuid4()), image_id=image_id, **entry) for entry in ais_data]
            session.add_all(records)


class ConstellationManager:
    def __init__(self, session_factory, db_handler):
        self.db_handler = db_handler
        self.session_factory = session_factory

    def _populate_constellations(self, satellite_config):
        with self.db_handler.session_scope() as session:
            for name, config in satellite_config.items():
                if not session.query(Constellation).filter_by(name=name).first():
                    session.add(
                        Constellation(
                            name=name,
                            description=f"{name} satellite constellation",
                            available_product_types=config["product_types"],
                            available_processing_levels=config["processing_levels"],
                            available_sensor_modes=config["sensor_modes"],
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
                    parameters=query_data["parameters"],
                )
            )
            return query_id


class DownloadManager:
    def __init__(self, session_factory, db_handler):
        self.db_handler = db_handler
        self.session_factory = session_factory

    def record_download(self, product_data: Dict[str, Any]):
        with self.db_handler.session_scope() as session:
            session.add(
                DownloadRecord(
                    product_id=product_data["product_id"],
                    query_id=product_data["query_id"],
                    constellation=product_data["constellation"],
                    sensor_mode=product_data["sensor_mode"],
                    product_type=product_data["product_type"],
                    processing_level=product_data["processing_level"],
                    status=product_data["status"],
                    file_path=str(product_data["file_path"]),
                    file_size_mb=product_data.get("file_size_mb"),
                    checksum=product_data.get("checksum"),
                    metadata=product_data.get("metadata"),
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
                    num_ship_detections=detection.get("num_detections"),
                    num_dark_ship_detections=detection.get("num_detections"),
                    latitude=detection.get("num_detections"),
                    longitude=detection.get("num_detections"),
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
                    )
                )
