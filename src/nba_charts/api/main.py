from typing import Annotated

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
from nba_charts.services.nba import get_shot_chart_records, render_shot_chart_image
from nba_charts.settings import SETTINGS


def _serialize_report_frame(records: list[dict[str, object]]) -> list[dict[str, object]]:
    cleaned_records: list[dict[str, object]] = []
    for row in records:
        cleaned_records.append({key: value for key, value in row.items() if key != "season_order"})
    return cleaned_records


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
