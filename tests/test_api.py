import os
from dataclasses import dataclass

import pandas as pd
from fastapi.testclient import TestClient

os.environ["NBA_CHARTS_KOBE_DATA_SOURCE"] = "file"

from nba_charts.api.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_echarts_page_is_served() -> None:
    response = client.get("/echarts/kobe-shot-poc")
    assert response.status_code == 200
    assert "Apache ECharts" in response.text
    assert "Kobe shot archive POC on ECharts" in response.text


def test_career_points_echarts_page_is_served() -> None:
    response = client.get("/echarts/career-points-race")
    assert response.status_code == 200
    assert "Career points race" in response.text


@dataclass(frozen=True)
class _FakeCareerPointsSnapshot:
    dataframe: pd.DataFrame
    backend: str
    detail: str


def test_career_points_race_endpoint_returns_frame_payload(monkeypatch) -> None:
    fake_frame = pd.DataFrame(
        [
            {
                "season_id": "1999-00",
                "season_start_year": 1999,
                "player_id": 2,
                "player_name": "Bravo",
                "team_abbreviation": "BBB",
                "season_points": 1700,
                "career_points": 1700,
                "season_points_rank": 1,
                "career_points_rank": 1,
            },
            {
                "season_id": "1999-00",
                "season_start_year": 1999,
                "player_id": 1,
                "player_name": "Alpha",
                "team_abbreviation": "AAA",
                "season_points": 1500,
                "career_points": 1500,
                "season_points_rank": 2,
                "career_points_rank": 2,
            },
        ]
    )

    monkeypatch.setattr(
        "nba_charts.api.main.load_career_points_frames_from_postgres",
        lambda: _FakeCareerPointsSnapshot(
            fake_frame, "postgres", "analytics.player_career_points_frames"
        ),
    )

    response = client.get("/api/reports/career-points-race", params={"top_n": 1})
    assert response.status_code == 200

    payload = response.json()
    assert payload["tool_option"] == "echarts-bar-race"
    assert payload["backend_source"] == "postgres"
    assert payload["seasons"] == ["1999-00"]
    assert payload["frames"][0]["leaders"][0]["player_name"] == "Bravo"


def test_fg3m_report_endpoint_returns_filtered_data() -> None:
    response = client.get("/api/reports/fg3m", params={"player_id": 101, "upto_season": "2001-02"})
    assert response.status_code == 200

    payload = response.json()
    assert payload["season"] == "2001-02"
    assert len(payload["records"]) == 2
    assert all(row["player_id"] == 101 for row in payload["records"])


def test_kobe_shot_poc_endpoint_returns_scope_and_view_summaries() -> None:
    response = client.get(
        "/api/reports/kobe-shot-poc",
        params=[("season", "2000-01"), ("shot_made_flag", 1), ("shot_made_flag", 0)],
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["tool_option"] == "dash-plotly"
    assert payload["supported_frontends"] == ["dash-plotly", "echarts"]
    assert payload["backend_source"] == "file"
    assert payload["season"] == "2000-01"
    assert payload["scope_summary"]["made_shots"] == 735
    assert payload["view_summary"]["visible_shots"] == 1575
    assert payload["records"][0]["shot_result"] in {"Made", "Missed"}
    assert payload["records"][0]["shot_made_flag"] in {0, 1}
