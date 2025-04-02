# database/utils/database/base.py

from sqlalchemy.orm import declarative_base, DeclarativeMeta
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import inspect
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from pydantic import field_validator
from pydantic import ValidationInfo


Base: DeclarativeMeta = declarative_base()


class BaseMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class Settings(BaseSettings):
    base_path: Path = Path("data")
    in_progress_dir: Path = Path("in_progress")
    completed_dir: Path = Path("completed")
    detections_dir: Path = Path("detections")
    ais_dir: Path = Path("AIS")

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @field_validator("in_progress_dir", "completed_dir", "detections_dir", "ais_dir", mode="after")
    @classmethod
    def resolve_subpaths(cls, v: Path, info: ValidationInfo) -> Path:
        # Access base_path after all fields are parsed
        base = info.data.get("base_path", Path("data"))
        return v if v.is_absolute() else base / v
