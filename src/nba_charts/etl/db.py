from pathlib import Path
from typing import Any, LiteralString, cast

from psycopg import connect
from psycopg.connection import Connection
from psycopg.sql import SQL

from nba_charts.settings import SETTINGS

SQL_ROOT = Path(__file__).resolve().parents[1] / "db" / "sql"


def get_connection(
    *,
    database_name: str | None = None,
    autocommit: bool = False,
    row_factory: Any | None = None,
) -> Connection:
    connection = connect(
        SETTINGS.build_dsn(database_name),
        autocommit=autocommit,
        connect_timeout=SETTINGS.db_connect_timeout_seconds,
        row_factory=row_factory,
    )
    return connection


def get_admin_connection(*, autocommit: bool = False) -> Connection:
    connection = connect(
        SETTINGS.admin_database_dsn,
        autocommit=autocommit,
        connect_timeout=SETTINGS.db_connect_timeout_seconds,
    )
    return connection


def load_sql(relative_path: str) -> str:
    return (SQL_ROOT / relative_path).read_text(encoding="utf-8")


def load_sql_query(relative_path: str) -> SQL:
    return SQL(cast(LiteralString, load_sql(relative_path)))


def execute_sql_file(connection: Connection, relative_path: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute(load_sql_query(relative_path))
