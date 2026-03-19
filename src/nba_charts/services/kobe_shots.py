from __future__ import annotations

from pathlib import Path

import pandas as pd

from nba_charts.services.datasets import season_sort_key
from nba_charts.settings import SETTINGS


def load_kobe_shot_dataset(path: Path | None = None) -> pd.DataFrame:
    dataset_path = path or SETTINGS.sample_kobe_shot_path
    dataframe = pd.read_csv(dataset_path)
    if dataframe.empty:
        return dataframe

    normalized = dataframe.copy()
    normalized["season"] = normalized["season"].astype(str)
    normalized["season_order"] = normalized["season"].map(season_sort_key)
    normalized["game_date"] = pd.to_datetime(normalized["game_date"], errors="coerce")
    normalized["playoffs"] = normalized["playoffs"].fillna(0).astype(int)
    normalized["shot_distance"] = pd.to_numeric(
        normalized["shot_distance"], errors="coerce"
    ).fillna(0)
    normalized["loc_x"] = pd.to_numeric(normalized["loc_x"], errors="coerce").fillna(0)
    normalized["loc_y"] = pd.to_numeric(normalized["loc_y"], errors="coerce").fillna(0)
    normalized["shot_made_flag"] = pd.to_numeric(
        normalized["shot_made_flag"], errors="coerce"
    ).astype("Int64")
    normalized["shot_result"] = normalized["shot_made_flag"].map({1: "Made", 0: "Missed"})
    normalized["shot_result"] = normalized["shot_result"].fillna("Unknown")
    normalized["points_value"] = (
        normalized["shot_type"].eq("3PT Field Goal").map({True: 3, False: 2})
    )
    normalized["game_date_label"] = normalized["game_date"].dt.strftime("%Y-%m-%d")
    return normalized.sort_values(["season_order", "game_date", "shot_id"]).reset_index(drop=True)


def kobe_season_list(dataframe: pd.DataFrame) -> list[str]:
    seasons = dataframe[["season", "season_order"]].drop_duplicates().sort_values("season_order")
    return seasons["season"].tolist()


def kobe_shot_zone_options(dataframe: pd.DataFrame) -> list[str]:
    zones = dataframe["shot_zone_basic"].dropna().drop_duplicates().sort_values()
    return zones.tolist()


def scope_kobe_shots(
    dataframe: pd.DataFrame,
    season: str | None = None,
    cumulative: bool = False,
    playoffs_only: bool = False,
) -> pd.DataFrame:
    filtered = dataframe.copy()
    seasons = kobe_season_list(filtered)
    active_season = season or (seasons[-1] if seasons else None)

    if active_season:
        if cumulative:
            filtered = filtered[filtered["season_order"] <= season_sort_key(active_season)]
        else:
            filtered = filtered[filtered["season"] == active_season]

    if playoffs_only:
        filtered = filtered[filtered["playoffs"] == 1]

    return filtered.reset_index(drop=True)


def filter_kobe_shots(
    dataframe: pd.DataFrame,
    season: str | None = None,
    cumulative: bool = False,
    shot_result: str = "Made",
    shot_made_flags: list[int] | None = None,
    zone_basics: list[str] | None = None,
    playoffs_only: bool = False,
) -> pd.DataFrame:
    filtered = scope_kobe_shots(
        dataframe,
        season=season,
        cumulative=cumulative,
        playoffs_only=playoffs_only,
    )

    if shot_made_flags is not None:
        filtered = filtered[filtered["shot_made_flag"].isin(shot_made_flags)]

    if shot_result == "Known":
        filtered = filtered[filtered["shot_result"] != "Unknown"]
    elif shot_result != "All":
        filtered = filtered[filtered["shot_result"] == shot_result]

    if zone_basics:
        filtered = filtered[filtered["shot_zone_basic"].isin(zone_basics)]

    return filtered.reset_index(drop=True)


def build_kobe_scope_summary(dataframe: pd.DataFrame) -> dict[str, int | float | str | None]:
    known = dataframe[dataframe["shot_result"] != "Unknown"]
    made = dataframe[dataframe["shot_result"] == "Made"]
    favorite_zone = "No made shots"
    favorite_zone_makes = 0

    if not made.empty:
        zone_counts = made["shot_zone_basic"].value_counts()
        favorite_zone = str(zone_counts.index[0])
        favorite_zone_makes = int(zone_counts.iloc[0])

    fg_pct = round((len(made) / len(known)) * 100, 1) if len(known) else None
    return {
        "attempts": int(len(dataframe)),
        "known_attempts": int(len(known)),
        "made_shots": int(len(made)),
        "fg_pct": fg_pct,
        "three_point_makes": int(made["points_value"].eq(3).sum()),
        "playoff_makes": int(made[made["playoffs"] == 1].shape[0]),
        "favorite_zone": favorite_zone,
        "favorite_zone_makes": favorite_zone_makes,
    }


def build_kobe_view_summary(dataframe: pd.DataFrame) -> dict[str, int]:
    return {
        "visible_shots": int(len(dataframe)),
        "visible_makes": int(dataframe["shot_result"].eq("Made").sum()),
        "visible_misses": int(dataframe["shot_result"].eq("Missed").sum()),
        "visible_unknown": int(dataframe["shot_result"].eq("Unknown").sum()),
    }


def build_kobe_zone_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return pd.DataFrame(
            columns=["shot_zone_basic", "visible_shots", "made_shots", "known_attempts", "fg_pct"]
        )

    summary = (
        dataframe.assign(
            known_shot=dataframe["shot_result"].ne("Unknown"),
            made_shot=dataframe["shot_result"].eq("Made"),
        )
        .groupby("shot_zone_basic", dropna=False)
        .agg(
            visible_shots=("shot_id", "count"),
            made_shots=("made_shot", "sum"),
            known_attempts=("known_shot", "sum"),
        )
        .reset_index()
    )

    summary["fg_pct"] = (
        (summary["made_shots"] / summary["known_attempts"] * 100)
        .where(summary["known_attempts"] > 0)
        .round(1)
    )
    return summary.sort_values(
        ["visible_shots", "shot_zone_basic"], ascending=[False, True]
    ).reset_index(drop=True)


def build_kobe_season_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return pd.DataFrame(
            columns=["season", "attempts", "known_attempts", "made_shots", "fg_pct"]
        )

    summary = (
        dataframe.assign(
            known_shot=dataframe["shot_result"].ne("Unknown"),
            made_shot=dataframe["shot_result"].eq("Made"),
        )
        .groupby(["season", "season_order"], dropna=False)
        .agg(
            attempts=("shot_id", "count"),
            known_attempts=("known_shot", "sum"),
            made_shots=("made_shot", "sum"),
        )
        .reset_index()
        .sort_values("season_order")
    )

    summary["fg_pct"] = (
        (summary["made_shots"] / summary["known_attempts"] * 100)
        .where(summary["known_attempts"] > 0)
        .round(1)
    )
    return summary.reset_index(drop=True)
