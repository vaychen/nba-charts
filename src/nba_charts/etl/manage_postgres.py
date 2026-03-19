from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence
from datetime import date
from typing import Any, cast

import pandas as pd
from psycopg.sql import SQL, Identifier

from nba_charts.etl.db import (
    execute_sql_file,
    get_admin_connection,
    get_connection,
    load_sql_query,
)
from nba_charts.etl.sync_reference import sync_all
from nba_charts.services.kobe_shots import KOBE_SHOT_BASE_COLUMNS, load_kobe_shot_dataset
from nba_charts.settings import SETTINGS

LOGGER = logging.getLogger(__name__)
DDL_FILES = [
    "ddl/database.sql",
    "ddl/players.sql",
    "ddl/teams.sql",
    "ddl/kobe_shots.sql",
]
KOBE_SHOT_UPSERT_COLUMNS = [
    "shot_id",
    "action_type",
    "combined_shot_type",
    "game_event_id",
    "game_id",
    "lat",
    "loc_x",
    "loc_y",
    "lon",
    "minutes_remaining",
    "period",
    "playoffs",
    "season",
    "seconds_remaining",
    "shot_distance",
    "shot_made_flag",
    "shot_type",
    "shot_zone_area",
    "shot_zone_basic",
    "shot_zone_range",
    "team_id",
    "team_name",
    "game_date",
    "matchup",
    "opponent",
]
KOBE_SAMPLE_SOURCE_NAME = "kobe_career_shoot_made.csv"


def ensure_database_exists() -> None:
    with get_admin_connection(autocommit=True) as connection, connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (SETTINGS.db_name,))
        exists = cursor.fetchone() is not None
        if exists:
            LOGGER.info("Database %s already exists", SETTINGS.db_name)
            return

        cursor.execute(SQL("CREATE DATABASE {}").format(Identifier(SETTINGS.db_name)))
        LOGGER.info("Created database %s", SETTINGS.db_name)


def bootstrap_database() -> None:
    ensure_database_exists()
    with get_connection() as connection:
        for relative_path in DDL_FILES:
            execute_sql_file(connection, relative_path)
        connection.commit()
    LOGGER.info("Applied DDL for stats and analytics schemas")


def _db_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.date()
    if hasattr(value, "item"):
        return value.item()
    if isinstance(value, date):
        return value
    return value


def load_kobe_shots() -> None:
    dataframe = load_kobe_shot_dataset()
    selected = dataframe[KOBE_SHOT_BASE_COLUMNS].copy()
    sql = load_sql_query("dml/kobe_shots.sql")
    rows = []
    selected_records = cast(Any, selected).to_dict(orient="records")

    for record in selected_records:
        row = [_db_value(record[column]) for column in KOBE_SHOT_UPSERT_COLUMNS]
        row.append(KOBE_SAMPLE_SOURCE_NAME)
        rows.append(tuple(row))

    with get_connection() as connection, connection.cursor() as cursor:
        cursor.executemany(sql, rows)
        connection.commit()
    LOGGER.info("Loaded %s Kobe shot rows into analytics.kobe_shots", len(rows))


def prepare_kobe_backend() -> None:
    bootstrap_database()
    sync_all()
    load_kobe_shots()
    LOGGER.info("Prepared local Postgres backend with stats reference data and Kobe shots")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the local PostgreSQL backend.")
    parser.add_argument(
        "action",
        choices=["bootstrap", "load-kobe-shots", "prepare-kobe-backend"],
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)

    actions = {
        "bootstrap": bootstrap_database,
        "load-kobe-shots": load_kobe_shots,
        "prepare-kobe-backend": prepare_kobe_backend,
    }
    actions[args.action]()


if __name__ == "__main__":
    main()
