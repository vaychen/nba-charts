from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd
from psycopg import Error as PsycopgError
from psycopg import OperationalError
from psycopg.errors import InvalidSchemaName, UndefinedTable
from psycopg.rows import dict_row

from nba_charts.etl.db import get_connection
from nba_charts.services.kobe_shots import (
    KOBE_SHOT_BASE_COLUMNS,
    load_kobe_shot_dataset,
    normalize_kobe_shot_dataframe,
)
from nba_charts.settings import SETTINGS

KobeDataSource = Literal["auto", "file", "postgres"]


@dataclass(frozen=True)
class KobeDataSnapshot:
    dataframe: pd.DataFrame
    backend: Literal["file", "postgres"]
    detail: str


class KobeBackendError(RuntimeError):
    """Raised when the requested Kobe backend cannot provide data."""


def load_kobe_shot_dataset_from_postgres() -> pd.DataFrame:
    query = """
        SELECT
            action_type,
            combined_shot_type,
            game_event_id,
            game_id,
            lat,
            loc_x,
            loc_y,
            lon,
            minutes_remaining,
            period,
            playoffs,
            season,
            seconds_remaining,
            shot_distance,
            shot_made_flag,
            shot_type,
            shot_zone_area,
            shot_zone_basic,
            shot_zone_range,
            team_id,
            team_name,
            game_date,
            matchup,
            opponent,
            shot_id
        FROM analytics.kobe_shots
        ORDER BY game_date, shot_id
    """

    with get_connection(row_factory=dict_row) as connection, connection.cursor() as cursor:
        cursor.execute(query)
        records = cursor.fetchall()

    if not records:
        return pd.DataFrame(columns=KOBE_SHOT_BASE_COLUMNS)

    dataframe = pd.DataFrame.from_records(records, columns=KOBE_SHOT_BASE_COLUMNS)
    return normalize_kobe_shot_dataframe(dataframe)


def load_kobe_data_snapshot(source: KobeDataSource | None = None) -> KobeDataSnapshot:
    requested_source = source or SETTINGS.kobe_data_source

    if requested_source == "file":
        return KobeDataSnapshot(
            dataframe=load_kobe_shot_dataset(),
            backend="file",
            detail=str(SETTINGS.sample_kobe_shot_path.name),
        )

    try:
        dataframe = load_kobe_shot_dataset_from_postgres()
    except (OperationalError, UndefinedTable, InvalidSchemaName, PsycopgError) as exc:
        if requested_source == "auto":
            return KobeDataSnapshot(
                dataframe=load_kobe_shot_dataset(),
                backend="file",
                detail=f"fallback:{exc.__class__.__name__}",
            )
        raise KobeBackendError(
            "Postgres backend is not ready. Run db bootstrap and load the Kobe sample first."
        ) from exc

    if dataframe.empty:
        if requested_source == "auto":
            return KobeDataSnapshot(
                dataframe=load_kobe_shot_dataset(),
                backend="file",
                detail="fallback:analytics.kobe_shots empty",
            )
        raise KobeBackendError("Postgres backend is empty. Run the Kobe sample load command first.")

    return KobeDataSnapshot(
        dataframe=dataframe,
        backend="postgres",
        detail="analytics.kobe_shots",
    )
