"""
SQLAlchemy Database Models and Handler for Satellite Product Tracking
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Optional, Generator
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
import pandas as pd

from database.util.base import Settings
from database.CONFIG import SATELLITE_CONFIG
from database.util.views import DatabaseViews
from database.util.base import Base
from database.util.tables import DownloadRecord
from database.util.managers import (
    ImageManager,
    DetectionManager,
    DownloadManager,
    ConstellationManager,
    QueryManager,
    AISManager,
)


CONSTELLATION_DETECTION_TABLES = {}
CONSTELLATION_IMAGE_TABLES = {}


class DatabaseHandler:
    def __init__(self, db_file: Optional[Path] = None, config: Optional[Settings] = None):
        self.config = config or Settings()
        #  self.db_path = self.config.base_path / "downloads.db"
        self.db_path = Path(db_file) if db_file else self.config.base_path / "downloads.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure parent dir exists

        # This points SQLAlchemy to the exact same file every time (unless settings.DOWNLOAD_DIR changes).
        # so if the file exists, it jsut reuse it.
        self.engine = create_engine(f"sqlite:///{self.db_path}", pool_pre_ping=True)
        self.session_factory = scoped_session(sessionmaker(bind=self.engine))
        self.views = DatabaseViews(self.engine, SATELLITE_CONFIG)  # Initialize DatabaseViews

        # Initialize managers
        self.image_manager = ImageManager(self.session_factory, self)
        self.detection_manager = DetectionManager(self.session_factory, self)
        self.download_manager = DownloadManager(self.session_factory, self)
        self.constellation_manager = ConstellationManager(self.session_factory, self)
        self.query_manager = QueryManager(self.session_factory, self)
        self.ais_manager = AISManager(self.session_factory, self)

        # Initialize the database
        self._init_db()
        self.constellation_manager._populate_constellations(SATELLITE_CONFIG)

        self.views._create_views()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope around a series of operations.
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _init_db(self):
        """
        Initialize the database by creating all required tables.
        """
        # only creates missing tables; it won’t drop or overwrite existing ones. (Because checkfirst=True by default.)
        Base.metadata.create_all(self.engine)  # registers 'images'
        self.constellation_manager._populate_constellations(SATELLITE_CONFIG)
        self.views._create_views()

    def get_download_history(self, days: int = 7) -> pd.DataFrame:
        """
        Retrieve the download history for the past `days` days.

        Args:
            days (int): Number of days to look back.

        Returns:
            pd.DataFrame: A DataFrame containing the download history.
        """
        with self.session_scope() as session:
            query = session.query(DownloadRecord).filter(DownloadRecord.download_time >= datetime.utcnow() - timedelta(days=days))
            return pd.read_sql(query.statement, session.bind)

    def is_downloaded(self, product_id: str) -> bool:
        """
        Check if a product has already been downloaded.

        Args:
            product_id (str): The ID of the product to check.

        Returns:
            bool: True if the product is downloaded, False otherwise.
        """
        with self.session_scope() as session:
            return session.query(DownloadRecord.product_id).filter_by(product_id=product_id).scalar() is not None
