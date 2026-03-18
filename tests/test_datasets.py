from nba_charts.services.datasets import (
    default_player_ids,
    leaderboard,
    load_fg3m_dataset,
    season_list,
)


def test_load_fg3m_dataset_has_expected_seasons() -> None:
    dataframe = load_fg3m_dataset()
    assert season_list(dataframe) == ["2000-01", "2001-02", "2002-03"]


def test_default_player_ids_prioritize_latest_leaders() -> None:
    dataframe = load_fg3m_dataset()
    assert default_player_ids(dataframe, limit=2) == [101, 102]


def test_leaderboard_returns_ranked_rows() -> None:
    dataframe = load_fg3m_dataset()
    ranked = leaderboard(dataframe, "2001-02")
    assert ranked.iloc[0]["player_name"] == "Blake B"
    assert ranked.iloc[0]["fg3m"] == 112
