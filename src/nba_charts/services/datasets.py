from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from nba_charts.settings import SETTINGS


def season_sort_key(season_id: str) -> int:
    return int(season_id.split("-")[0])


def load_fg3m_dataset(path: Path | None = None) -> pd.DataFrame:
    dataset_path = path or SETTINGS.sample_fg3m_path
    records = json.loads(dataset_path.read_text(encoding="utf-8"))
    dataframe = pd.DataFrame.from_records(records)
    if dataframe.empty:
        return dataframe

    dataframe["season_id"] = dataframe["season_id"].astype(str)
    dataframe["player_id"] = dataframe["player_id"].astype(int)
    dataframe["fg3m"] = dataframe["fg3m"].astype(int)
    dataframe["season_order"] = dataframe["season_id"].map(season_sort_key)
    return dataframe.sort_values(["season_order", "fg3m"], ascending=[True, False]).reset_index(
        drop=True
    )


def season_list(dataframe: pd.DataFrame) -> list[str]:
    seasons = dataframe[["season_id", "season_order"]].drop_duplicates().sort_values("season_order")
    return seasons["season_id"].tolist()


def default_player_ids(dataframe: pd.DataFrame, limit: int = 3) -> list[int]:
    seasons = season_list(dataframe)
    if not seasons:
        return []
    latest_season = seasons[-1]
    latest_rows = dataframe[dataframe["season_id"] == latest_season]
    ranked = latest_rows.sort_values("fg3m", ascending=False).head(limit)
    return ranked["player_id"].astype(int).tolist()


def filter_fg3m_dataset(
    dataframe: pd.DataFrame,
    player_ids: list[int] | None = None,
    upto_season: str | None = None,
) -> pd.DataFrame:
    filtered = dataframe.copy()

    if player_ids:
        filtered = filtered[filtered["player_id"].isin(player_ids)]

    if upto_season:
        filtered = filtered[filtered["season_order"] <= season_sort_key(upto_season)]

    return filtered.reset_index(drop=True)


def leaderboard(
    dataframe: pd.DataFrame,
    season_id: str,
    player_ids: list[int] | None = None,
    top_n: int = 8,
) -> pd.DataFrame:
    filtered = dataframe[dataframe["season_id"] == season_id]
    if player_ids:
        filtered = filtered[filtered["player_id"].isin(player_ids)]
    ranked = filtered.sort_values("fg3m", ascending=False).head(top_n)
    return ranked.reset_index(drop=True)


def player_options(dataframe: pd.DataFrame) -> list[dict[str, int | str]]:
    players = dataframe[["player_id", "player_name"]].drop_duplicates().sort_values("player_name")
    return [
        {"label": row.player_name, "value": int(row.player_id)}
        for row in players.itertuples(index=False)
    ]
