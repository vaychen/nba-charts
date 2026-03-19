import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
PACKAGE_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")


def _int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return int(raw_value)


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
    db_user: str
    db_password: str
    sample_fg3m_path: Path
    sample_kobe_shot_path: Path

    @property
    def database_dsn(self) -> str:
        if self.db_dsn:
            return self.db_dsn
        return (
            f"dbname={self.db_name} user={self.db_user} password={self.db_password} "
            f"host={self.db_host} port={self.db_port}"
        )


def get_settings() -> Settings:
    return Settings(
        api_host=os.getenv("NBA_CHARTS_API_HOST", "127.0.0.1"),
        api_port=_int_env("NBA_CHARTS_API_PORT", 8000),
        dashboard_host=os.getenv("NBA_CHARTS_DASH_HOST", "127.0.0.1"),
        dashboard_port=_int_env("NBA_CHARTS_DASH_PORT", 8050),
        dashboard_interval_ms=_int_env("NBA_CHARTS_DASH_INTERVAL_MS", 1200),
        db_dsn=os.getenv("NBA_CHARTS_DB_DSN") or None,
        db_host=os.getenv("NBA_CHARTS_DB_HOST", "localhost"),
        db_port=_int_env("NBA_CHARTS_DB_PORT", 5432),
        db_name=os.getenv("NBA_CHARTS_DB_NAME", "nba_charts"),
        db_user=os.getenv("NBA_CHARTS_DB_USER", "postgres"),
        db_password=os.getenv("NBA_CHARTS_DB_PASSWORD", "postgres"),
        sample_fg3m_path=ROOT_DIR / "data" / "sample" / "fg3m_by_season_sample.json",
        sample_kobe_shot_path=ROOT_DIR / "data" / "sample" / "kobe_career_shoot_made.csv",
    )


SETTINGS = get_settings()
