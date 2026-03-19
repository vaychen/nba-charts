from typing import Annotated, Literal

import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from nba_charts.services.datasets import (
    filter_fg3m_dataset,
    leaderboard,
    load_fg3m_dataset,
    season_list,
)
from nba_charts.services.kobe_shots import (
    build_kobe_scope_summary,
    build_kobe_season_summary,
    build_kobe_view_summary,
    build_kobe_zone_summary,
    filter_kobe_shots,
    kobe_season_list,
    kobe_shot_zone_options,
    load_kobe_shot_dataset,
    scope_kobe_shots,
)
from nba_charts.services.nba import get_shot_chart_records, render_shot_chart_image
from nba_charts.settings import SETTINGS

KOBE_DATAFRAME = load_kobe_shot_dataset()
KOBE_SEASON_SUMMARY = build_kobe_season_summary(KOBE_DATAFRAME)


def _serialize_report_frame(records: list[dict[str, object]]) -> list[dict[str, object]]:
    cleaned_records: list[dict[str, object]] = []
    for row in records:
        cleaned_records.append({key: value for key, value in row.items() if key != "season_order"})
    return cleaned_records


def _serialize_dataframe_records(dataframe, columns: list[str]) -> list[dict[str, object]]:
    if dataframe.empty:
        return []
    selected = dataframe[columns].copy()
    selected = selected.where(selected.notna(), None)
    return selected.to_dict(orient="records")


def create_app() -> FastAPI:
    app = FastAPI(title="NBA Charts API", version="0.2.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root() -> dict[str, str]:
        return {"message": "NBA Charts API"}

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/reports/fg3m")
    def fg3m_report(
        player_id: Annotated[list[int] | None, Query()] = None,
        upto_season: str | None = None,
    ) -> dict[str, object]:
        dataframe = load_fg3m_dataset()
        seasons = season_list(dataframe)
        if not seasons:
            return {"season": None, "seasons": [], "records": [], "leaderboard": []}

        active_season = upto_season or seasons[-1]
        filtered = filter_fg3m_dataset(dataframe, player_ids=player_id, upto_season=active_season)
        ranked = leaderboard(dataframe, season_id=active_season, player_ids=player_id)

        return {
            "season": active_season,
            "seasons": seasons,
            "records": _serialize_report_frame(filtered.to_dict(orient="records")),
            "leaderboard": _serialize_report_frame(ranked.to_dict(orient="records")),
        }

    @app.get("/api/reports/kobe-shot-poc")
    def kobe_shot_poc(
        season: str | None = None,
        cumulative: bool = False,
        shot_result: Literal["Made", "Missed", "Unknown", "Known", "All"] = "Made",
        playoffs_only: bool = False,
        zone: Annotated[list[str] | None, Query()] = None,
    ) -> dict[str, object]:
        seasons = kobe_season_list(KOBE_DATAFRAME)
        active_season = season or (seasons[-1] if seasons else None)
        if not active_season:
            return {
                "season": None,
                "available_seasons": [],
                "available_zones": [],
                "scope_summary": {},
                "view_summary": {},
                "season_summary": [],
                "zone_summary": [],
                "records": [],
            }

        scope_df = scope_kobe_shots(
            KOBE_DATAFRAME,
            season=active_season,
            cumulative=cumulative,
            playoffs_only=playoffs_only,
        )
        view_df = filter_kobe_shots(
            KOBE_DATAFRAME,
            season=active_season,
            cumulative=cumulative,
            shot_result=shot_result,
            zone_basics=zone,
            playoffs_only=playoffs_only,
        )
        zone_summary = build_kobe_zone_summary(view_df)

        return {
            "season": active_season,
            "cumulative": cumulative,
            "shot_result": shot_result,
            "playoffs_only": playoffs_only,
            "tool_option": "dash-plotly",
            "available_seasons": seasons,
            "available_zones": kobe_shot_zone_options(KOBE_DATAFRAME),
            "scope_summary": build_kobe_scope_summary(scope_df),
            "view_summary": build_kobe_view_summary(view_df),
            "season_summary": _serialize_dataframe_records(
                KOBE_SEASON_SUMMARY,
                ["season", "attempts", "known_attempts", "made_shots", "fg_pct"],
            ),
            "zone_summary": _serialize_dataframe_records(
                zone_summary,
                ["shot_zone_basic", "visible_shots", "made_shots", "known_attempts", "fg_pct"],
            ),
            "records": _serialize_dataframe_records(
                view_df,
                [
                    "shot_id",
                    "season",
                    "game_date_label",
                    "matchup",
                    "opponent",
                    "shot_type",
                    "shot_zone_basic",
                    "shot_zone_area",
                    "shot_zone_range",
                    "shot_distance",
                    "playoffs",
                    "loc_x",
                    "loc_y",
                    "shot_result",
                    "points_value",
                ],
            ),
        }

    @app.get("/api/shot-chart")
    def shot_chart(player_id: int, season: str) -> dict[str, object]:
        data = get_shot_chart_records(player_id, season)
        return {"player_id": player_id, "season": season, "data": data}

    @app.get("/api/shot-chart/image")
    def shot_chart_image(player_id: int, season: str) -> StreamingResponse:
        buffer = render_shot_chart_image(player_id, season)
        return StreamingResponse(buffer, media_type="image/png")

    return app


app = create_app()


def run() -> None:
    uvicorn.run(app, host=SETTINGS.api_host, port=SETTINGS.api_port)
