from __future__ import annotations

import math

import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html
from plotly.subplots import make_subplots

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
from nba_charts.settings import SETTINGS

DATAFRAME = load_kobe_shot_dataset()
SEASONS = kobe_season_list(DATAFRAME)
SHOT_ZONES = kobe_shot_zone_options(DATAFRAME)
SEASON_SUMMARY = build_kobe_season_summary(DATAFRAME)

RESULT_COLORS = {
    "Made": "#C6842F",
    "Missed": "#8B4C39",
    "Unknown": "#65727D",
}
BODY_FONT = "Trebuchet MS, Verdana, sans-serif"
DISPLAY_FONT = "Georgia, Times New Roman, serif"


def _arc_path(
    center_x: float,
    center_y: float,
    radius: float,
    start_degrees: float,
    end_degrees: float,
    steps: int = 60,
) -> str:
    path_points: list[str] = []
    for step in range(steps + 1):
        angle = math.radians(start_degrees + (end_degrees - start_degrees) * step / steps)
        x_value = center_x + radius * math.cos(angle)
        y_value = center_y + radius * math.sin(angle)
        command = "M" if step == 0 else "L"
        path_points.append(f"{command} {x_value:.1f},{y_value:.1f}")
    return " ".join(path_points)


def _court_shapes() -> list[dict[str, object]]:
    court_color = "#9B6A3A"
    return [
        {
            "type": "circle",
            "x0": -7.5,
            "x1": 7.5,
            "y0": -7.5,
            "y1": 7.5,
            "line": {"color": court_color, "width": 2},
        },
        {
            "type": "line",
            "x0": -30,
            "x1": 30,
            "y0": -7.5,
            "y1": -7.5,
            "line": {"color": court_color, "width": 2},
        },
        {
            "type": "rect",
            "x0": -80,
            "x1": 80,
            "y0": -47.5,
            "y1": 143,
            "line": {"color": court_color, "width": 2},
        },
        {
            "type": "rect",
            "x0": -60,
            "x1": 60,
            "y0": -47.5,
            "y1": 143,
            "line": {"color": court_color, "width": 2},
        },
        {
            "type": "path",
            "path": _arc_path(0, 143, 60, 0, 180),
            "line": {"color": court_color, "width": 2},
        },
        {
            "type": "path",
            "path": _arc_path(0, 0, 40, 0, 180),
            "line": {"color": court_color, "width": 2},
        },
        {
            "type": "line",
            "x0": -220,
            "x1": -220,
            "y0": -47.5,
            "y1": 92.5,
            "line": {"color": court_color, "width": 2},
        },
        {
            "type": "line",
            "x0": 220,
            "x1": 220,
            "y0": -47.5,
            "y1": 92.5,
            "line": {"color": court_color, "width": 2},
        },
        {
            "type": "path",
            "path": _arc_path(0, 0, 237.5, 22, 158),
            "line": {"color": court_color, "width": 2},
        },
    ]


def _metric_card(title: str, value_id: str, detail_id: str) -> html.Div:
    return html.Div(
        [
            html.P(
                title,
                style={
                    "margin": "0 0 10px",
                    "fontSize": "0.82rem",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.08em",
                    "color": "#7F6956",
                },
            ),
            html.H2(
                id=value_id,
                style={
                    "margin": "0 0 8px",
                    "fontFamily": DISPLAY_FONT,
                    "fontSize": "2rem",
                    "color": "#2A211C",
                },
            ),
            html.P(id=detail_id, style={"margin": "0", "fontSize": "0.95rem", "color": "#615246"}),
        ],
        style={
            "background": "rgba(255, 250, 239, 0.84)",
            "border": "1px solid rgba(142, 102, 62, 0.16)",
            "borderRadius": "20px",
            "padding": "18px",
            "boxShadow": "0 18px 38px rgba(74, 49, 28, 0.08)",
        },
    )


def _empty_figure(title: str, message: str) -> go.Figure:
    figure = go.Figure()
    figure.update_layout(
        title=title,
        paper_bgcolor="#FFF9ED",
        plot_bgcolor="#FFF9ED",
        margin={"l": 40, "r": 20, "t": 70, "b": 40},
        font={"family": BODY_FONT, "color": "#2A211C"},
    )
    figure.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"size": 16, "color": "#615246"},
    )
    return figure


def build_shot_chart_figure(
    view_df, active_season: str, cumulative: bool, shot_result: str, zone_count: int
) -> go.Figure:
    title_prefix = "Career through" if cumulative else "Season"
    title_suffix = f"{shot_result} view" if shot_result != "All" else "All outcomes"
    figure = go.Figure()

    if view_df.empty:
        empty = _empty_figure(
            title=f"Kobe shot map - {title_prefix} {active_season}",
            message="No shots match the current filters.",
        )
        empty.update_layout(shapes=_court_shapes())
        empty.update_xaxes(range=[-260, 260], visible=False)
        empty.update_yaxes(range=[-60, 430], visible=False, scaleanchor="x", scaleratio=1)
        return empty

    for result in ["Made", "Missed", "Unknown"]:
        result_df = view_df[view_df["shot_result"] == result]
        if result_df.empty:
            continue

        figure.add_trace(
            go.Scattergl(
                x=result_df["loc_x"],
                y=result_df["loc_y"],
                mode="markers",
                name=result,
                customdata=result_df[
                    [
                        "game_date_label",
                        "matchup",
                        "opponent",
                        "shot_type",
                        "shot_zone_basic",
                        "shot_distance",
                    ]
                ],
                marker={
                    "size": 8 if result == "Made" else 7,
                    "color": RESULT_COLORS[result],
                    "opacity": 0.76 if result == "Made" else 0.58,
                    "line": {"color": "#FFF9ED", "width": 0.5},
                },
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>Date: %{customdata[0]}<br>Matchup: %{customdata[1]}"
                    "<br>Opponent: %{customdata[2]}<br>Shot: %{customdata[3]}"
                    "<br>Zone: %{customdata[4]}<br>Distance: %{customdata[5]} ft.<extra></extra>"
                ),
            )
        )

    figure.update_layout(
        title=f"Kobe shot map - {title_prefix} {active_season} ({title_suffix})",
        paper_bgcolor="#FFF9ED",
        plot_bgcolor="#F7E8C8",
        margin={"l": 20, "r": 20, "t": 70, "b": 20},
        font={"family": BODY_FONT, "color": "#2A211C"},
        legend={"orientation": "h", "y": 1.05, "x": 0},
        shapes=_court_shapes(),
        annotations=[
            {
                "x": 0.5,
                "y": 1.05,
                "xref": "paper",
                "yref": "paper",
                "text": f"{len(view_df):,} shots in view across {zone_count} court zones",
                "showarrow": False,
                "font": {"size": 12, "color": "#6D5D4B"},
            }
        ],
    )
    figure.update_xaxes(range=[-260, 260], visible=False)
    figure.update_yaxes(range=[-60, 430], visible=False, scaleanchor="x", scaleratio=1)
    return figure


def build_zone_figure(zone_summary, shot_result: str) -> go.Figure:
    if zone_summary.empty:
        return _empty_figure("Court zones", "Try widening the result or zone filters.")

    title = "Made shots by zone" if shot_result == "Made" else "Visible shots by zone"
    figure = go.Figure(
        go.Bar(
            x=zone_summary["visible_shots"],
            y=zone_summary["shot_zone_basic"],
            orientation="h",
            marker={"color": "#B66E28"},
            customdata=zone_summary[["made_shots", "known_attempts", "fg_pct"]],
            text=zone_summary["visible_shots"],
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>Shots in view: %{x}<br>Made shots: %{customdata[0]}"
                "<br>Known attempts: %{customdata[1]}<br>FG%%: %{customdata[2]}<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        title=title,
        paper_bgcolor="#FFF9ED",
        plot_bgcolor="#FFF9ED",
        margin={"l": 40, "r": 20, "t": 70, "b": 40},
        font={"family": BODY_FONT, "color": "#2A211C"},
    )
    figure.update_xaxes(title_text="Shots in current view", gridcolor="#E6D4B5")
    figure.update_yaxes(title_text="Zone", autorange="reversed")
    return figure


def build_trend_figure(active_season: str) -> go.Figure:
    if SEASON_SUMMARY.empty:
        return _empty_figure("Career trend", "No season summary is available.")

    bar_colors = [
        "#B66E28" if season == active_season else "#E2C18E" for season in SEASON_SUMMARY["season"]
    ]
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.add_trace(
        go.Bar(
            x=SEASON_SUMMARY["season"],
            y=SEASON_SUMMARY["made_shots"],
            name="Made shots",
            marker={"color": bar_colors},
            hovertemplate="Season: %{x}<br>Made shots: %{y}<extra></extra>",
        ),
        secondary_y=False,
    )
    figure.add_trace(
        go.Scatter(
            x=SEASON_SUMMARY["season"],
            y=SEASON_SUMMARY["fg_pct"],
            name="FG% on known shots",
            mode="lines+markers",
            line={"color": "#4D3C31", "width": 3},
            marker={"size": 8, "color": "#4D3C31"},
            hovertemplate="Season: %{x}<br>FG%%: %{y}<extra></extra>",
        ),
        secondary_y=True,
    )
    figure.update_layout(
        title="Career rhythm by season",
        paper_bgcolor="#FFF9ED",
        plot_bgcolor="#FFF9ED",
        margin={"l": 40, "r": 40, "t": 70, "b": 50},
        font={"family": BODY_FONT, "color": "#2A211C"},
        legend={"orientation": "h", "y": 1.1, "x": 0},
    )
    figure.update_xaxes(title_text="Season", showgrid=False)
    figure.update_yaxes(title_text="Made shots", gridcolor="#E6D4B5", secondary_y=False)
    figure.update_yaxes(title_text="FG%", secondary_y=True, rangemode="tozero")
    return figure


def create_app() -> Dash:
    app = Dash(__name__)
    app.title = "NBA Charts | Kobe Shot POC"
    initial_season_index = len(SEASONS) - 1 if SEASONS else 0

    app.layout = html.Div(
        style={
            "minHeight": "100vh",
            "padding": "28px 22px 42px",
            "background": "linear-gradient(180deg, #E8D1A5 0%, #F5ECD8 42%, #FAF6EE 100%)",
            "fontFamily": BODY_FONT,
        },
        children=[
            html.Div(
                [
                    html.Div(
                        [
                            html.P(
                                "NBA Charts",
                                style={
                                    "margin": "0 0 8px",
                                    "letterSpacing": "0.18em",
                                    "textTransform": "uppercase",
                                    "color": "#8A5C2F",
                                },
                            ),
                            html.H1(
                                "Kobe shot archive POC",
                                style={
                                    "margin": "0 0 10px",
                                    "fontFamily": DISPLAY_FONT,
                                    "fontSize": "clamp(2.4rem, 5vw, 4rem)",
                                    "color": "#2A211C",
                                },
                            ),
                            html.P(
                                (
                                    "First tool option: Dash + Plotly. This prototype turns the "
                                    "sample Kobe shot file into a scrubbable shot map, zone view, "
                                    "and season rhythm panel."
                                ),
                                style={
                                    "maxWidth": "760px",
                                    "margin": "0",
                                    "fontSize": "1.02rem",
                                    "lineHeight": "1.6",
                                    "color": "#5F5041",
                                },
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.P(
                                "Sample notes",
                                style={
                                    "margin": "0 0 10px",
                                    "textTransform": "uppercase",
                                    "letterSpacing": "0.1em",
                                    "fontSize": "0.76rem",
                                    "color": "#7A634F",
                                },
                            ),
                            html.P(
                                "30,697 shots across 20 seasons",
                                style={"margin": "0 0 6px", "fontSize": "1rem", "color": "#2A211C"},
                            ),
                            html.P(
                                "5,000 rows still have unknown outcomes in the source sample",
                                style={"margin": "0", "fontSize": "0.95rem", "color": "#5F5041"},
                            ),
                        ],
                        style={
                            "background": "rgba(255, 250, 239, 0.78)",
                            "border": "1px solid rgba(138, 92, 47, 0.16)",
                            "borderRadius": "20px",
                            "padding": "18px",
                            "minWidth": "260px",
                            "boxShadow": "0 18px 38px rgba(74, 49, 28, 0.08)",
                        },
                    ),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))",
                    "gap": "18px",
                    "alignItems": "start",
                    "marginBottom": "20px",
                },
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.P(
                                        "Season track",
                                        style={
                                            "margin": "0 0 8px",
                                            "textTransform": "uppercase",
                                            "letterSpacing": "0.1em",
                                            "fontSize": "0.8rem",
                                            "color": "#7A634F",
                                        },
                                    ),
                                    html.P(
                                        id="kobe-season-focus",
                                        style={
                                            "margin": "0",
                                            "fontSize": "1.25rem",
                                            "fontWeight": "600",
                                            "color": "#2A211C",
                                        },
                                    ),
                                ]
                            ),
                            html.Button(
                                "Play",
                                id="kobe-play-button",
                                n_clicks=0,
                                style={
                                    "background": "#7A4A24",
                                    "color": "#FFF9ED",
                                    "border": "0",
                                    "borderRadius": "999px",
                                    "padding": "11px 18px",
                                    "cursor": "pointer",
                                    "fontWeight": "600",
                                },
                            ),
                        ],
                        style={
                            "display": "flex",
                            "justifyContent": "space-between",
                            "gap": "14px",
                            "alignItems": "center",
                            "marginBottom": "12px",
                        },
                    ),
                    dcc.Slider(
                        id="kobe-season-slider",
                        min=0,
                        max=initial_season_index,
                        step=None,
                        value=initial_season_index,
                        marks={index: season for index, season in enumerate(SEASONS)},
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label(
                                        "View mode",
                                        style={"display": "block", "marginBottom": "8px"},
                                    ),
                                    dcc.RadioItems(
                                        id="kobe-scope-mode",
                                        options=[
                                            {"label": "Season snapshot", "value": "season"},
                                            {"label": "Cumulative career", "value": "cumulative"},
                                        ],
                                        value="season",
                                        inline=True,
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Shot result",
                                        style={"display": "block", "marginBottom": "8px"},
                                    ),
                                    dcc.RadioItems(
                                        id="kobe-shot-result",
                                        options=[
                                            {"label": option, "value": option}
                                            for option in [
                                                "Made",
                                                "Known",
                                                "All",
                                                "Missed",
                                                "Unknown",
                                            ]
                                        ],
                                        value="Made",
                                        inline=True,
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Court zones",
                                        style={"display": "block", "marginBottom": "8px"},
                                    ),
                                    dcc.Dropdown(
                                        id="kobe-zone-filter",
                                        options=[
                                            {"label": zone, "value": zone} for zone in SHOT_ZONES
                                        ],
                                        multi=True,
                                        placeholder="All zones",
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Sample constraint",
                                        style={"display": "block", "marginBottom": "8px"},
                                    ),
                                    dcc.Checklist(
                                        id="kobe-playoffs-only",
                                        options=[{"label": "Playoffs only", "value": "playoffs"}],
                                        value=[],
                                    ),
                                ]
                            ),
                        ],
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(auto-fit, minmax(240px, 1fr))",
                            "gap": "16px",
                            "marginTop": "18px",
                            "color": "#2A211C",
                        },
                    ),
                    dcc.Interval(
                        id="kobe-season-interval",
                        interval=SETTINGS.dashboard_interval_ms,
                        n_intervals=0,
                        disabled=True,
                    ),
                    dcc.Store(id="kobe-is-playing", data=False),
                    html.P(
                        id="kobe-summary-note",
                        style={"margin": "16px 0 0", "color": "#5F5041", "lineHeight": "1.5"},
                    ),
                ],
                style={
                    "background": "rgba(255, 250, 239, 0.86)",
                    "border": "1px solid rgba(138, 92, 47, 0.16)",
                    "borderRadius": "22px",
                    "padding": "18px",
                    "boxShadow": "0 20px 40px rgba(74, 49, 28, 0.08)",
                    "marginBottom": "18px",
                },
            ),
            html.Div(
                [
                    _metric_card(
                        "Shots in current view", "kobe-visible-shots", "kobe-visible-detail"
                    ),
                    _metric_card("Made shots in scope", "kobe-made-shots", "kobe-made-detail"),
                    _metric_card("FG% on known shots", "kobe-fg-pct", "kobe-fg-detail"),
                    _metric_card(
                        "Three-point makes", "kobe-three-point-makes", "kobe-three-point-detail"
                    ),
                    _metric_card(
                        "Favorite make zone", "kobe-favorite-zone", "kobe-favorite-zone-detail"
                    ),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))",
                    "gap": "14px",
                    "marginBottom": "18px",
                },
            ),
            html.Div(
                [
                    dcc.Graph(id="kobe-shot-chart", config={"displayModeBar": False}),
                    dcc.Graph(id="kobe-zone-chart", config={"displayModeBar": False}),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": "minmax(0, 1.45fr) minmax(320px, 0.95fr)",
                    "gap": "16px",
                },
            ),
            html.Div(
                dcc.Graph(id="kobe-trend-chart", config={"displayModeBar": False}),
                style={
                    "marginTop": "16px",
                    "background": "rgba(255, 250, 239, 0.72)",
                    "border": "1px solid rgba(138, 92, 47, 0.12)",
                    "borderRadius": "20px",
                    "padding": "10px",
                },
            ),
        ],
    )

    @app.callback(
        Output("kobe-is-playing", "data"),
        Output("kobe-season-interval", "disabled"),
        Output("kobe-play-button", "children"),
        Input("kobe-play-button", "n_clicks"),
        State("kobe-is-playing", "data"),
    )
    def toggle_playback(n_clicks: int, is_playing: bool) -> tuple[bool, bool, str]:
        if not n_clicks:
            return False, True, "Play"

        next_state = not is_playing
        return next_state, not next_state, "Pause" if next_state else "Play"

    @app.callback(
        Output("kobe-season-slider", "value"),
        Input("kobe-season-interval", "n_intervals"),
        State("kobe-season-slider", "value"),
        prevent_initial_call=True,
    )
    def advance_season(_: int, slider_value: int) -> int:
        if not SEASONS:
            return 0
        if slider_value >= len(SEASONS) - 1:
            return 0
        return slider_value + 1

    @app.callback(
        Output("kobe-shot-chart", "figure"),
        Output("kobe-zone-chart", "figure"),
        Output("kobe-trend-chart", "figure"),
        Output("kobe-season-focus", "children"),
        Output("kobe-summary-note", "children"),
        Output("kobe-visible-shots", "children"),
        Output("kobe-visible-detail", "children"),
        Output("kobe-made-shots", "children"),
        Output("kobe-made-detail", "children"),
        Output("kobe-fg-pct", "children"),
        Output("kobe-fg-detail", "children"),
        Output("kobe-three-point-makes", "children"),
        Output("kobe-three-point-detail", "children"),
        Output("kobe-favorite-zone", "children"),
        Output("kobe-favorite-zone-detail", "children"),
        Input("kobe-season-slider", "value"),
        Input("kobe-scope-mode", "value"),
        Input("kobe-shot-result", "value"),
        Input("kobe-zone-filter", "value"),
        Input("kobe-playoffs-only", "value"),
    )
    def update_dashboard(
        slider_value: int,
        scope_mode: str,
        shot_result: str,
        zone_basics: list[str] | None,
        playoffs_flags: list[str],
    ) -> tuple[
        go.Figure,
        go.Figure,
        go.Figure,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
        str,
    ]:
        if not SEASONS:
            empty_figure = _empty_figure("Kobe shot POC", "No shot data is available.")
            return (
                empty_figure,
                empty_figure,
                empty_figure,
                "Season focus: unavailable",
                "No Kobe sample data was found.",
                "0",
                "No filtered shots",
                "0",
                "No made shots in scope",
                "n/a",
                "No known attempts in scope",
                "0",
                "No made threes in scope",
                "n/a",
                "No favorite zone available",
            )

        active_season = SEASONS[slider_value]
        cumulative = scope_mode == "cumulative"
        playoffs_only = "playoffs" in playoffs_flags
        scope_df = scope_kobe_shots(
            DATAFRAME,
            season=active_season,
            cumulative=cumulative,
            playoffs_only=playoffs_only,
        )
        view_df = filter_kobe_shots(
            DATAFRAME,
            season=active_season,
            cumulative=cumulative,
            shot_result=shot_result,
            zone_basics=zone_basics or None,
            playoffs_only=playoffs_only,
        )
        scope_summary = build_kobe_scope_summary(scope_df)
        view_summary = build_kobe_view_summary(view_df)
        zone_summary = build_kobe_zone_summary(view_df)
        trend_figure = build_trend_figure(active_season)
        shot_chart_figure = build_shot_chart_figure(
            view_df,
            active_season=active_season,
            cumulative=cumulative,
            shot_result=shot_result,
            zone_count=len(zone_summary),
        )
        zone_figure = build_zone_figure(zone_summary, shot_result=shot_result)

        focus_label = (
            f"Career through {active_season}" if cumulative else f"Season focus: {active_season}"
        )
        unknown_count = int(scope_summary["attempts"] - scope_summary["known_attempts"])
        note = (
            f"Scope includes {scope_summary['attempts']:,} shots and "
            f"{scope_summary['known_attempts']:,} known outcomes; "
            f"{unknown_count:,} rows still have withheld results in the sample."
        )
        if playoffs_only:
            note += " Playoff mode is active."
        if zone_basics:
            note += f" Zone filter narrowed the view to {len(zone_basics)} court zones."

        fg_pct = scope_summary["fg_pct"]
        fg_pct_value = f"{fg_pct:.1f}%" if isinstance(fg_pct, float) else "n/a"
        favorite_zone = str(scope_summary["favorite_zone"])
        favorite_zone_makes = int(scope_summary["favorite_zone_makes"])
        return (
            shot_chart_figure,
            zone_figure,
            trend_figure,
            focus_label,
            note,
            f"{view_summary['visible_shots']:,}",
            f"{view_summary['visible_makes']:,} makes, {view_summary['visible_misses']:,} misses",
            f"{scope_summary['made_shots']:,}",
            f"{scope_summary['playoff_makes']:,} came in playoffs",
            fg_pct_value,
            f"Across {scope_summary['known_attempts']:,} known attempts in scope",
            f"{scope_summary['three_point_makes']:,}",
            "Long-range makes inside the selected scope",
            favorite_zone,
            f"{favorite_zone_makes:,} makes came from this zone",
        )

    return app


def run() -> None:
    app = create_app()
    app.run(host=SETTINGS.dashboard_host, port=str(SETTINGS.dashboard_port + 1), debug=True)


if __name__ == "__main__":
    run()
