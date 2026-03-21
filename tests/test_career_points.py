import pandas as pd

from nba_charts.services.career_points import (
    build_career_points_frames,
    build_career_points_payload,
    normalize_season_points_dataframe,
)


def test_normalize_season_points_dataframe_shapes_league_leader_rows() -> None:
    raw = pd.DataFrame(
        [
            {
                "PLAYER_ID": 1,
                "RANK": 2,
                "PLAYER": "Player One",
                "TEAM_ID": 10,
                "TEAM": "AAA",
                "GP": 80,
                "PTS": 1600,
            }
        ]
    )

    normalized = normalize_season_points_dataframe(raw, "2000-01")
    assert normalized.loc[0, "season_id"] == "2000-01"
    assert int(normalized.loc[0, "season_start_year"]) == 2000
    assert int(normalized.loc[0, "pts"]) == 1600
    assert int(normalized.loc[0, "season_points_rank"]) == 2


def test_build_career_points_frames_accumulates_points_by_player() -> None:
    season_points = pd.DataFrame(
        [
            {
                "season_id": "1999-00",
                "season_start_year": 1999,
                "player_id": 1,
                "player_name": "Alpha",
                "team_abbreviation": "AAA",
                "gp": 80,
                "pts": 1500,
                "season_points_rank": 2,
            },
            {
                "season_id": "1999-00",
                "season_start_year": 1999,
                "player_id": 2,
                "player_name": "Bravo",
                "team_abbreviation": "BBB",
                "gp": 82,
                "pts": 1700,
                "season_points_rank": 1,
            },
            {
                "season_id": "2000-01",
                "season_start_year": 2000,
                "player_id": 1,
                "player_name": "Alpha",
                "team_abbreviation": "AAA",
                "gp": 82,
                "pts": 1800,
                "season_points_rank": 1,
            },
            {
                "season_id": "2000-01",
                "season_start_year": 2000,
                "player_id": 2,
                "player_name": "Bravo",
                "team_abbreviation": "BBB",
                "gp": 79,
                "pts": 1400,
                "season_points_rank": 2,
            },
        ]
    )

    frames = build_career_points_frames(season_points)
    alpha_second = frames[(frames["season_id"] == "2000-01") & (frames["player_id"] == 1)].iloc[0]
    bravo_second = frames[(frames["season_id"] == "2000-01") & (frames["player_id"] == 2)].iloc[0]

    assert int(alpha_second["career_points"]) == 3300
    assert int(bravo_second["career_points"]) == 3100
    assert int(alpha_second["career_points_rank"]) == 1


def test_build_career_points_frames_carries_retired_players_forward() -> None:
    season_points = pd.DataFrame(
        [
            {
                "season_id": "1999-00",
                "season_start_year": 1999,
                "player_id": 1,
                "player_name": "Alpha",
                "team_abbreviation": "AAA",
                "gp": 80,
                "pts": 2500,
                "season_points_rank": 1,
            },
            {
                "season_id": "1999-00",
                "season_start_year": 1999,
                "player_id": 2,
                "player_name": "Bravo",
                "team_abbreviation": "BBB",
                "gp": 82,
                "pts": 1900,
                "season_points_rank": 2,
            },
            {
                "season_id": "2000-01",
                "season_start_year": 2000,
                "player_id": 2,
                "player_name": "Bravo",
                "team_abbreviation": "BBB",
                "gp": 79,
                "pts": 1200,
                "season_points_rank": 3,
            },
            {
                "season_id": "2000-01",
                "season_start_year": 2000,
                "player_id": 3,
                "player_name": "Charlie",
                "team_abbreviation": "CCC",
                "gp": 81,
                "pts": 1800,
                "season_points_rank": 1,
            },
        ]
    )

    frames = build_career_points_frames(season_points)
    alpha_second = frames[(frames["season_id"] == "2000-01") & (frames["player_id"] == 1)].iloc[0]
    bravo_second = frames[(frames["season_id"] == "2000-01") & (frames["player_id"] == 2)].iloc[0]
    charlie_second = frames[(frames["season_id"] == "2000-01") & (frames["player_id"] == 3)].iloc[0]

    assert int(alpha_second["season_points"]) == 0
    assert int(alpha_second["career_points"]) == 2500
    assert int(alpha_second["career_points_rank"]) == 2
    assert int(bravo_second["career_points"]) == 3100
    assert int(bravo_second["career_points_rank"]) == 1
    assert int(charlie_second["career_points"]) == 1800


def test_build_career_points_payload_includes_top_rows_by_season() -> None:
    frames = pd.DataFrame(
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
            {
                "season_id": "2000-01",
                "season_start_year": 2000,
                "player_id": 1,
                "player_name": "Alpha",
                "team_abbreviation": "AAA",
                "season_points": 1800,
                "career_points": 3300,
                "season_points_rank": 1,
                "career_points_rank": 1,
            },
            {
                "season_id": "2000-01",
                "season_start_year": 2000,
                "player_id": 2,
                "player_name": "Bravo",
                "team_abbreviation": "BBB",
                "season_points": 1400,
                "career_points": 3100,
                "season_points_rank": 2,
                "career_points_rank": 2,
            },
        ]
    )

    payload = build_career_points_payload(frames, top_n=1)
    assert payload["seasons"] == ["1999-00", "2000-01"]
    assert len(payload["frames"]) == 2
    assert payload["frames"][1]["leaders"][0]["player_name"] == "Alpha"
