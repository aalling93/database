# database/utils/database/base.py

from sqlalchemy.orm import declarative_base, DeclarativeMeta
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import inspect
from pydantic_settings import BaseSettings

from pathlib import Path
from pydantic import field_validator

Base: DeclarativeMeta = declarative_base()


class BaseMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


class Settings(BaseSettings):
    # Directory configuration
    DOWNLOAD_DIR: Path = Path("data")
    IN_PROGRESS_DIR: Path = Path("in_progress")
    COMPLETED_DIR: Path = Path("completed")

    # model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore")

    @field_validator("IN_PROGRESS_DIR", "COMPLETED_DIR", mode="before")
    @classmethod
    def resolve_paths(cls, value: Path, values: dict) -> Path:
        return values.data["DOWNLOAD_DIR"] / value
