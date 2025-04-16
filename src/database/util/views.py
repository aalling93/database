from sqlalchemy import text


class DatabaseViews:
    def __init__(self, engine, satellite_config):
        """
        Initialize the DatabaseViews class.

        Args:
            engine: SQLAlchemy engine for database connection.
            satellite_config: Configuration dictionary for satellite constellations.
        """
        self.engine = engine
        self.satellite_config = satellite_config

    def _create_views(self):
        with self.engine.connect() as conn:
            # Drop global views
            conn.execute(text("DROP VIEW IF EXISTS image_counts_by_constellation"))
            conn.execute(text("DROP VIEW IF EXISTS detection_counts_by_constellation"))
            conn.execute(text("DROP VIEW IF EXISTS latest_image_per_constellation"))
            conn.execute(text("DROP VIEW IF EXISTS detection_summary_by_image"))
            conn.execute(text("DROP VIEW IF EXISTS download_summary_by_status"))
            # Drop AIS-related views if they exist
            conn.execute(text("DROP VIEW IF EXISTS ais_records_with_image_info"))
            conn.execute(text("DROP VIEW IF EXISTS ais_summary_by_image"))

            # Create per-constellation views
            for name in self.satellite_config:
                safe_name = name.lower().replace("-", "_")
                view_img = f"{safe_name}_images"
                view_det = f"{safe_name}_detections"

                conn.execute(text(f"DROP VIEW IF EXISTS {view_img}"))
                conn.execute(
                    text(
                        f"""
                    CREATE VIEW {view_img} AS
                    SELECT * FROM images WHERE constellation = '{name}'
                """
                    )
                )

                conn.execute(text(f"DROP VIEW IF EXISTS {view_det}"))
                conn.execute(
                    text(
                        f"""
                    CREATE VIEW {view_det} AS
                    SELECT * FROM detections WHERE constellation = '{name}'
                """
                    )
                )

                #
                # View: detection summary per constellation
                conn.execute(text(f"DROP VIEW IF EXISTS detection_summary_{safe_name}"))
                conn.execute(
                    text(
                        f"""
                        CREATE VIEW detection_summary_{safe_name} AS
                        SELECT
                            constellation,
                            COUNT(*) AS num_detections,
                            COUNT(DISTINCT image_id) AS num_images,
                            ROUND(AVG(num_ship_detections), 2) AS avg_detections_per_image
                        FROM detections
                        WHERE constellation = '{name}'
                        GROUP BY constellation;
                    """
                    )
                )

                # View: object summary per constellation
                conn.execute(text(f"DROP VIEW IF EXISTS object_summary_{safe_name}"))
                conn.execute(
                    text(
                        f"""
                        CREATE VIEW object_summary_{safe_name} AS
                        SELECT
                            d.constellation,
                            COUNT(o.id) AS num_objects,
                            ROUND(AVG(o.length_min), 2) AS avg_length_min,
                            ROUND(AVG(o.length_max), 2) AS avg_length_max,
                            ROUND(AVG(o.speed_min), 2) AS avg_speed_min,
                            ROUND(AVG(o.speed_max), 2) AS avg_speed_max,
                            ROUND(AVG(o.distance_to_shore), 2) AS avg_distance_to_shore
                        FROM objects o
                        JOIN detections d ON o.image_id = d.image_id
                        WHERE d.constellation = '{name}'
                        GROUP BY d.constellation;
                    """
                    )
                )

            # Create global views
            conn.execute(
                text(
                    """
                CREATE VIEW image_counts_by_constellation AS
                SELECT constellation, COUNT(*) AS num_images
                FROM images
                GROUP BY constellation
            """
                )
            )

            conn.execute(
                text(
                    """
                CREATE VIEW detection_counts_by_constellation AS
                SELECT constellation, COUNT(*) AS num_detections
                FROM detections
                GROUP BY constellation
            """
                )
            )

            conn.execute(
                text(
                    """
                CREATE VIEW latest_image_per_constellation AS
                SELECT constellation, MAX(acquisition_time) AS latest_time
                FROM images
                GROUP BY constellation
            """
                )
            )

            conn.execute(
                text(
                    """
                CREATE VIEW detection_summary_by_image AS
                SELECT image_id, COUNT(id) AS num_detections, AVG(avg_confidence) AS avg_confidence
                FROM detections
                GROUP BY image_id
            """
                )
            )

            conn.execute(
                text(
                    """
                CREATE VIEW download_summary_by_status AS
                SELECT constellation, status, COUNT(*) AS num_downloads
                FROM downloads
                GROUP BY constellation, status
            """
                )
            )
            # Full AIS records enriched with image info
            conn.execute(
                text(
                    """
                CREATE VIEW ais_records_with_image_info AS
                SELECT
                    ais.id AS ais_id,
                    ais.image_id,
                    i.constellation,
                    i.acquisition_time,
                    i.file_path,
                    ais.mmsi,
                    ais.timestamp,
                    ais.latitude,
                    ais.longitude,
                    ais.speed,
                    ais.heading,
                    ais.status,
                    ais.source
                FROM ais
                JOIN images i ON ais.image_id = i.id;
            """
                )
            )

            # Summary of AIS records per image
            conn.execute(
                text(
                    """
                CREATE VIEW ais_summary_by_image AS
                SELECT
                    i.id AS image_id,
                    i.constellation,
                    COUNT(a.id) AS num_ais_records,
                    MIN(a.timestamp) AS earliest_ais_time,
                    MAX(a.timestamp) AS latest_ais_time,
                    AVG(a.speed) AS avg_speed
                FROM images i
                LEFT JOIN ais a ON i.id = a.image_id
                GROUP BY i.id, i.constellation;
            """
                )
            )
