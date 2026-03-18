from pathlib import Path

from psycopg import connect
from psycopg.connection import Connection

from nba_charts.settings import SETTINGS

SQL_ROOT = Path(__file__).resolve().parents[1] / "db" / "sql"


def get_connection() -> Connection:
    return connect(SETTINGS.database_dsn)


def load_sql(relative_path: str) -> str:
    return (SQL_ROOT / relative_path).read_text(encoding="utf-8")
