from io import BytesIO
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from nba_api.stats.endpoints.shotchartdetail import ShotChartDetail

SHOT_CHART_COLUMNS = ["LOC_X", "LOC_Y", "ACTION_TYPE", "SHOT_MADE_FLAG"]


def fetch_shot_chart_dataframe(player_id: int, season: str) -> pd.DataFrame:
    shot_chart = ShotChartDetail(
        team_id=0,
        player_id=player_id,
        season_nullable=season,
        season_type_all_star="Regular Season",
    )
    shot_dataframe = shot_chart.shot_chart_detail.get_data_frame()
    return shot_dataframe[SHOT_CHART_COLUMNS].copy()


def get_shot_chart_records(player_id: int, season: str) -> list[dict[str, Any]]:
    dataframe = fetch_shot_chart_dataframe(player_id, season)
    return dataframe.to_dict(orient="records")


def render_shot_chart_image(player_id: int, season: str) -> BytesIO:
    dataframe = fetch_shot_chart_dataframe(player_id, season)
    made_shots = dataframe[dataframe["SHOT_MADE_FLAG"] == 1]
    missed_shots = dataframe[dataframe["SHOT_MADE_FLAG"] == 0]

    figure, axis = plt.subplots(figsize=(9, 8))
    axis.scatter(missed_shots["LOC_X"], missed_shots["LOC_Y"], color="#D96C6C", alpha=0.45, s=18)
    axis.scatter(made_shots["LOC_X"], made_shots["LOC_Y"], color="#1F7A8C", alpha=0.65, s=22)
    axis.set_title(f"Shot Chart: {player_id} - {season}")
    axis.set_xlabel("Court X")
    axis.set_ylabel("Court Y")
    axis.set_xlim(-260, 260)
    axis.set_ylim(-60, 430)
    axis.set_aspect("equal", adjustable="box")
    axis.grid(alpha=0.15)

    buffer = BytesIO()
    figure.tight_layout()
    figure.savefig(buffer, format="png", dpi=150)
    plt.close(figure)
    buffer.seek(0)
    return buffer
