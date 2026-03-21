import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
PACKAGE_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")


def _int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return int(raw_value)


def _bool_env(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def _lower_env(name: str, default: str) -> str:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower()


def _kobe_data_source_env() -> Literal["auto", "file", "postgres"]:
    raw_value = _lower_env("NBA_CHARTS_KOBE_DATA_SOURCE", "auto")
    if raw_value in {"auto", "file", "postgres"}:
        return cast(Literal["auto", "file", "postgres"], raw_value)
    return "auto"


@dataclass(frozen=True)
class Settings:
    api_host: str
    api_port: int
    dashboard_host: str
    dashboard_port: int
    dashboard_interval_ms: int
    db_dsn: str | None
    db_host: str
    db_port: int
    db_name: str
    db_admin_name: str
    db_user: str
    db_password: str
    db_connect_timeout_seconds: int
    nba_api_timeout_seconds: int
    nba_api_verify_ssl: bool
    kobe_data_source: Literal["auto", "file", "postgres"]
    sample_fg3m_path: Path
    sample_kobe_shot_path: Path

    def build_dsn(self, db_name: str | None = None) -> str:
        if self.db_dsn and db_name is None:
            return self.db_dsn

        database_name = db_name or self.db_name
        return (
            f"dbname={database_name} user={self.db_user} password={self.db_password} "
            f"host={self.db_host} port={self.db_port}"
        )

    @property
    def database_dsn(self) -> str:
        return self.build_dsn()

    @property
    def admin_database_dsn(self) -> str:
        return self.build_dsn(self.db_admin_name)


def get_settings() -> Settings:
    return Settings(
        api_host=os.getenv("NBA_CHARTS_API_HOST", "127.0.0.1"),
        api_port=_int_env("NBA_CHARTS_API_PORT", 8000),
        dashboard_host=os.getenv("NBA_CHARTS_DASH_HOST", "127.0.0.1"),
        dashboard_port=_int_env("NBA_CHARTS_DASH_PORT", 8050),
        dashboard_interval_ms=_int_env("NBA_CHARTS_DASH_INTERVAL_MS", 1200),
        db_dsn=os.getenv("NBA_CHARTS_DB_DSN") or None,
        db_host=os.getenv("NBA_CHARTS_DB_HOST", "127.0.0.1"),
        db_port=_int_env("NBA_CHARTS_DB_PORT", 5432),
        db_name=os.getenv("NBA_CHARTS_DB_NAME", "nba_charts"),
        db_admin_name=os.getenv("NBA_CHARTS_DB_ADMIN_NAME", "postgres"),
        db_user=os.getenv("NBA_CHARTS_DB_USER", "postgres"),
        db_password=os.getenv("NBA_CHARTS_DB_PASSWORD", "postgres"),
        db_connect_timeout_seconds=_int_env("NBA_CHARTS_DB_CONNECT_TIMEOUT_SECONDS", 10),
        nba_api_timeout_seconds=_int_env("NBA_CHARTS_NBA_API_TIMEOUT_SECONDS", 30),
        nba_api_verify_ssl=_bool_env("NBA_CHARTS_NBA_API_VERIFY_SSL", False),
        kobe_data_source=_kobe_data_source_env(),
        sample_fg3m_path=ROOT_DIR / "data" / "sample" / "fg3m_by_season_sample.json",
        sample_kobe_shot_path=ROOT_DIR / "data" / "sample" / "kobe_career_shoot_made.csv",
    )


SETTINGS = get_settings()
