import os

from fastapi.testclient import TestClient

os.environ["NBA_CHARTS_KOBE_DATA_SOURCE"] = "file"

from nba_charts.api.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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
    assert payload["backend_source"] == "file"
    assert payload["season"] == "2000-01"
    assert payload["scope_summary"]["made_shots"] == 735
    assert payload["view_summary"]["visible_shots"] == 1575
    assert payload["records"][0]["shot_result"] in {"Made", "Missed"}
