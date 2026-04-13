from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, cast

import pandas as pd
from psycopg import Error as PsycopgError
from psycopg import OperationalError
from psycopg.errors import InvalidSchemaName, UndefinedTable
from psycopg.rows import dict_row

from nba_charts.etl.db import get_connection

FIRST_CAREER_POINTS_SEASON_START = 1958


@dataclass(frozen=True)
class CareerPointsSnapshot:
    dataframe: pd.DataFrame
    backend: str
    detail: str


def season_id_from_start_year(start_year: int) -> str:
    return f"{start_year}-{str((start_year + 1) % 100).zfill(2)}"


def season_start_year(season_id: str) -> int:
    return int(season_id.split("-")[0])


def current_nba_season_start_year(today: datetime | None = None) -> int:
    current_date = today or datetime.now()
    return current_date.year if current_date.month >= 9 else current_date.year - 1


def supported_career_points_seasons(end_year: int | None = None) -> list[str]:
    final_year = end_year or current_nba_season_start_year()
    return [
        season_id_from_start_year(start_year)
        for start_year in range(FIRST_CAREER_POINTS_SEASON_START, final_year + 1)
    ]


def normalize_season_points_dataframe(dataframe: pd.DataFrame, season_id: str) -> pd.DataFrame:
    normalized = dataframe.copy()
    normalized["season_id"] = season_id
    normalized["season_start_year"] = season_start_year(season_id)
    normalized = normalized.rename(
        columns={
            "PLAYER_ID": "player_id",
            "RANK": "season_points_rank",
            "PLAYER": "player_name",
            "TEAM_ID": "team_id",
            "TEAM": "team_abbreviation",
            "GP": "gp",
            "PTS": "pts",
        }
    )
    integer_columns = [
        "player_id",
        "season_points_rank",
        "team_id",
        "gp",
        "pts",
        "season_start_year",
    ]
    for column in integer_columns:
        numeric_values = cast(Any, pd.to_numeric(normalized[column], errors="coerce"))
        normalized[column] = numeric_values.fillna(0).astype(int)
    selected = normalized[
        [
            "season_id",
            "season_start_year",
            "player_id",
            "player_name",
            "team_id",
            "team_abbreviation",
            "gp",
            "pts",
            "season_points_rank",
        ]
    ]
    return (
        cast(Any, selected)
        .sort_values(["season_start_year", "season_points_rank", "player_id"])
        .reset_index(drop=True)
    )


def build_career_points_frames(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return pd.DataFrame(
            {
                "season_id": pd.Series(dtype="object"),
                "season_start_year": pd.Series(dtype="int64"),
                "player_id": pd.Series(dtype="int64"),
                "player_name": pd.Series(dtype="object"),
                "team_abbreviation": pd.Series(dtype="object"),
                "season_points": pd.Series(dtype="int64"),
                "career_points": pd.Series(dtype="int64"),
                "season_points_rank": pd.Series(dtype="int64"),
                "career_points_rank": pd.Series(dtype="int64"),
            }
        )

    normalized = cast(Any, dataframe.copy()).sort_values(
        ["season_start_year", "season_points_rank", "player_id"]
    )
    season_records = cast(list[dict[str, Any]], normalized.to_dict(orient="records"))

    player_totals: dict[int, int] = {}
    player_names: dict[int, str] = {}
    player_teams: dict[int, str] = {}
    frame_rows: list[dict[str, int | str]] = []

    seasons = sorted({str(row["season_id"]) for row in season_records}, key=season_start_year)
    records_by_season: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in season_records:
        records_by_season[str(row["season_id"])].append(row)

    for season_id in seasons:
        season_rows = records_by_season[season_id]
        season_start = season_start_year(season_id)
        active_points: dict[int, int] = {}
        active_ranks: dict[int, int] = {}

        for row in season_rows:
            player_id = int(row["player_id"])
            season_points = int(row["pts"])
            player_totals[player_id] = player_totals.get(player_id, 0) + season_points
            player_names[player_id] = str(row["player_name"])
            player_teams[player_id] = str(row["team_abbreviation"])
            active_points[player_id] = season_points
            active_ranks[player_id] = int(row["season_points_rank"])

        ranking_rows = sorted(
            player_totals.items(),
            key=lambda item: (-item[1], player_names.get(item[0], ""), item[0]),
        )

        previous_points: int | None = None
        previous_rank = 0
        for index, (player_id, career_points) in enumerate(ranking_rows, start=1):
            if career_points != previous_points:
                previous_rank = index
                previous_points = career_points

            frame_rows.append(
                {
                    "season_id": season_id,
                    "season_start_year": season_start,
                    "player_id": player_id,
                    "player_name": player_names[player_id],
                    "team_abbreviation": player_teams.get(player_id, ""),
                    "season_points": active_points.get(player_id, 0),
                    "career_points": career_points,
                    "season_points_rank": active_ranks.get(player_id, 0),
                    "career_points_rank": previous_rank,
                }
            )

    return (
        pd.DataFrame.from_records(frame_rows)
        .sort_values(["season_start_year", "career_points_rank", "player_id"])
        .reset_index(drop=True)
    )


def load_career_points_frames_from_postgres() -> CareerPointsSnapshot:
    query = """
        SELECT
            season_id,
            season_start_year,
            player_id,
            player_name,
            team_abbreviation,
            season_points,
            career_points,
            season_points_rank,
            career_points_rank
        FROM analytics.player_career_points_frames
        ORDER BY season_start_year, career_points_rank, player_id
    """
    try:
        with get_connection(row_factory=dict_row) as connection, connection.cursor() as cursor:
            cursor.execute(query)
            records = cursor.fetchall()
    except (OperationalError, UndefinedTable, InvalidSchemaName, PsycopgError):
        return CareerPointsSnapshot(
            dataframe=pd.DataFrame(),
            backend="postgres",
            detail="analytics.player_career_points_frames unavailable",
        )

    dataframe = pd.DataFrame.from_records(records)
    if dataframe.empty:
        return CareerPointsSnapshot(
            dataframe=dataframe,
            backend="postgres",
            detail="analytics.player_career_points_frames empty",
        )
    return CareerPointsSnapshot(
        dataframe=dataframe,
        backend="postgres",
        detail="analytics.player_career_points_frames",
    )


def build_career_points_payload(
    dataframe: pd.DataFrame,
    *,
    top_n: int = 12,
    highlight_player_id: int | None = None,
) -> dict[str, Any]:
    if dataframe.empty:
        return {
            "seasons": [],
            "frames": [],
            "highlight_player_id": highlight_player_id,
            "top_n": top_n,
        }

    frames_by_season: dict[str, list[dict[str, Any]]] = defaultdict(list)
    sorted_frame = dataframe.sort_values(["season_start_year", "career_points_rank", "player_id"])
    for row in sorted_frame.to_dict(orient="records"):
        frames_by_season[str(row["season_id"])].append(row)

    seasons = list(frames_by_season.keys())
    frames: list[dict[str, Any]] = []
    for season in seasons:
        season_rows = frames_by_season[season]
        leaders = season_rows[:top_n]
        if highlight_player_id is not None and all(
            row["player_id"] != highlight_player_id for row in leaders
        ):
            highlight_row = next(
                (row for row in season_rows if row["player_id"] == highlight_player_id),
                None,
            )
            if highlight_row is not None:
                leaders = leaders[:-1] + [highlight_row]
                leaders = sorted(
                    leaders, key=lambda row: (row["career_points_rank"], row["player_id"])
                )

        frames.append(
            {
                "season": season,
                "leaders": [
                    {
                        "player_id": int(row["player_id"]),
                        "player_name": str(row["player_name"]),
                        "team_abbreviation": str(row["team_abbreviation"]),
                        "season_points": int(row["season_points"]),
                        "career_points": int(row["career_points"]),
                        "season_points_rank": int(row["season_points_rank"]),
                        "career_points_rank": int(row["career_points_rank"]),
                    }
                    for row in leaders
                ],
            }
        )

    return {
        "seasons": seasons,
        "frames": frames,
        "highlight_player_id": highlight_player_id,
        "top_n": top_n,
    }
