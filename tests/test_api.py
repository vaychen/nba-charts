from fastapi.testclient import TestClient

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
