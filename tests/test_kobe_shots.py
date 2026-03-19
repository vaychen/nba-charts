from nba_charts.services.kobe_shots import (
    build_kobe_scope_summary,
    build_kobe_zone_summary,
    filter_kobe_shots,
    kobe_season_list,
    load_kobe_shot_dataset,
    scope_kobe_shots,
)


def test_load_kobe_shot_dataset_spans_full_career() -> None:
    dataframe = load_kobe_shot_dataset()
    seasons = kobe_season_list(dataframe)
    assert seasons[:3] == ["1996-97", "1997-98", "1998-99"]
    assert seasons[-3:] == ["2013-14", "2014-15", "2015-16"]
    assert len(seasons) == 20


def test_filter_kobe_shots_can_focus_on_makes_for_one_season() -> None:
    dataframe = load_kobe_shot_dataset()
    filtered = filter_kobe_shots(dataframe, season="2000-01", shot_result="Made")
    assert len(filtered) == 735
    assert filtered["shot_result"].eq("Made").all()


def test_build_kobe_scope_summary_uses_known_attempts() -> None:
    dataframe = load_kobe_shot_dataset()
    scoped = scope_kobe_shots(dataframe, season="2000-01")
    summary = build_kobe_scope_summary(scoped)
    assert summary["attempts"] == 1868
    assert summary["known_attempts"] == 1575
    assert summary["made_shots"] == 735
    assert summary["fg_pct"] == 46.7
    assert summary["favorite_zone"] == "Mid-Range"


def test_build_kobe_zone_summary_prioritizes_busiest_zone() -> None:
    dataframe = load_kobe_shot_dataset()
    filtered = filter_kobe_shots(dataframe, season="2000-01", shot_result="Made")
    summary = build_kobe_zone_summary(filtered)
    assert summary.iloc[0]["shot_zone_basic"] == "Mid-Range"
    assert int(summary.iloc[0]["visible_shots"]) == 298
