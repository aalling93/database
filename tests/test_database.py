from datetime import datetime, timedelta
from pathlib import Path

import shutil
import pytest
from database.database_handler import DatabaseHandler
from database.util.tables import ImageRecord, DetectionRecord, AISRecord

from database.util.base import Settings


@pytest.fixture(scope="module")
def temp_db():
    # Setup temporary DB
    temp_dir = Path("data/temp_test_data")
    temp_dir.mkdir(exist_ok=True)
    settings = Settings()
    settings.DOWNLOAD_DIR = temp_dir
    db = DatabaseHandler(settings)
    yield db  # test functions will receive this
    shutil.rmtree(temp_dir)  # teardown


def insert_test_product(db, product_id: str, constellation: str, ais_count: int = 0):
    image_data = {
        "id": product_id,
        "constellation": constellation,
        "acquisition_time": datetime.utcnow(),
        "file_path": db.config.DOWNLOAD_DIR / f"{product_id}.tif",
    }
    db.image_manager.register_image(image_data)

    detection_data = {
        "image_id": product_id,
        "constellation": constellation,
        "detection_file": db.config.DOWNLOAD_DIR / f"{product_id}_detections.json",
        "num_detections": 42,
        "avg_confidence": 0.87,
        "stats": {"mean_area": 12.4, "std_dev_area": 3.2},
    }
    db.detection_manager.record_detection(detection_data)

    if ais_count > 0:
        now = datetime.utcnow()
        ais_data = [
            {
                "mmsi": f"219000{idx}",
                "timestamp": now - timedelta(seconds=idx * 15),
                "latitude": 57.3 + idx * 0.01,
                "longitude": 12.4 + idx * 0.01,
                "speed": 12.0 + idx,
                "heading": 45.0 + idx,
                "status": "under way",
                "source": "satellite",
            }
            for idx in range(ais_count)
        ]
        db.ais_manager.insert_ais_records(image_id=product_id, ais_data=ais_data)


def test_insert_sent1_product_with_ais(temp_db):
    insert_test_product(temp_db, "TEST_SENTINEL_001", "SENTINEL-1", ais_count=5)

    with temp_db.session_scope() as s:
        assert s.query(ImageRecord).count() >= 1
        assert s.query(DetectionRecord).count() >= 1
        assert s.query(AISRecord).count() >= 5


def test_insert_rcm_product_with_ais(temp_db):
    insert_test_product(temp_db, "TEST_RCM_001", "RCM", ais_count=2)

    with temp_db.session_scope() as s:
        s.query(AISRecord).filter_by(image_id="TEST_RCM_001").count() == 2


def test_insert_product_without_ais(temp_db):
    insert_test_product(temp_db, "TEST_NOAIS_001", "SENTINEL-1", ais_count=0)

    with temp_db.session_scope() as s:
        assert s.query(AISRecord).filter_by(image_id="TEST_NOAIS_001").count() == 0
