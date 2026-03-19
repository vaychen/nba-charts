import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc, html

from nba_charts.services.datasets import (
    default_player_ids,
    filter_fg3m_dataset,
    leaderboard,
    load_fg3m_dataset,
    player_options,
    season_list,
)
from nba_charts.settings import SETTINGS

DATAFRAME = load_fg3m_dataset()
SEASONS = season_list(DATAFRAME)
DEFAULT_PLAYER_IDS = default_player_ids(DATAFRAME)
PLAYER_OPTIONS = player_options(DATAFRAME)


def build_history_figure(selected_ids: list[int], active_season: str) -> go.Figure:
    filtered = filter_fg3m_dataset(DATAFRAME, player_ids=selected_ids, upto_season=active_season)
    figure = go.Figure()

    for _player_id, group in filtered.groupby("player_id"):
        name = group["player_name"].iloc[0]
        avatar_url = group["avatar_url"].iloc[0]
        figure.add_trace(
            go.Scatter(
                x=group["season_id"],
                y=group["fg3m"],
                mode="lines+markers",
                name=name,
                customdata=[[avatar_url] for _ in range(len(group))],
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>Season: %{x}<br>FG3M: %{y}"
                    "<br>Avatar: %{customdata[0]}<extra></extra>"
                ),
            )
        )

    figure.update_layout(
        title="Rolling 3PT history",
        margin={"l": 40, "r": 20, "t": 60, "b": 40},
        paper_bgcolor="#F7F4ED",
        plot_bgcolor="#FFFDF8",
        hovermode="x unified",
        legend_title_text="Players",
    )
    figure.update_xaxes(title_text="Season", showgrid=False)
    figure.update_yaxes(title_text="FG3M", gridcolor="#E5DED0")
    return figure


def build_leaderboard_figure(selected_ids: list[int], active_season: str) -> go.Figure:
    ranked = leaderboard(
        DATAFRAME, season_id=active_season, player_ids=selected_ids or None, top_n=8
    )

    figure = go.Figure(
        go.Bar(
            x=ranked["fg3m"],
            y=ranked["player_name"],
            orientation="h",
            marker={"color": "#C26D34"},
            hovertemplate="<b>%{y}</b><br>FG3M: %{x}<extra></extra>",
        )
    )
    figure.update_layout(
        title=f"Season leaderboard - {active_season}",
        margin={"l": 40, "r": 20, "t": 60, "b": 40},
        paper_bgcolor="#F7F4ED",
        plot_bgcolor="#FFFDF8",
    )
    figure.update_xaxes(title_text="FG3M", gridcolor="#E5DED0")
    figure.update_yaxes(title_text="Player", autorange="reversed")
    return figure


def create_app() -> Dash:
    app = Dash(__name__)
    initial_season_index = len(SEASONS) - 1 if SEASONS else 0

    app.layout = html.Div(
        style={"backgroundColor": "#F1ECE2", "minHeight": "100vh", "padding": "24px"},
        children=[
            html.Div(
                [
                    html.P("NBA Charts", style={"letterSpacing": "0.18em", "color": "#8A5A44"}),
                    html.H1("Dynamic 3PT report", style={"marginTop": "0", "color": "#2F3E46"}),
                    html.P(
                        (
                            "Use the player filter and season playback controls to inspect "
                            "how leaderboard order shifts over time."
                        ),
                        style={"maxWidth": "760px", "color": "#5C6770"},
                    ),
                ],
                style={"marginBottom": "20px"},
            ),
            html.Div(
                style={
                    "backgroundColor": "#FFFDF8",
                    "borderRadius": "16px",
                    "padding": "18px",
                    "boxShadow": "0 10px 30px rgba(47, 62, 70, 0.08)",
                    "marginBottom": "18px",
                },
                children=[
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(auto-fit, minmax(240px, 1fr))",
                            "gap": "16px",
                            "alignItems": "end",
                        },
                        children=[
                            html.Div(
                                [
                                    html.Label(
                                        "Players", style={"display": "block", "marginBottom": "8px"}
                                    ),
                                    dcc.Dropdown(
                                        id="player-select",
                                        options=PLAYER_OPTIONS,
                                        value=DEFAULT_PLAYER_IDS,
                                        multi=True,
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.Label(
                                        "Playback",
                                        style={"display": "block", "marginBottom": "8px"},
                                    ),
                                    html.Button(
                                        "Play",
                                        id="play-button",
                                        n_clicks=0,
                                        style={
                                            "backgroundColor": "#2F6B5F",
                                            "color": "white",
                                            "border": "0",
                                            "padding": "10px 16px",
                                            "borderRadius": "999px",
                                            "cursor": "pointer",
                                        },
                                    ),
                                ]
                            ),
                            html.Div(
                                id="season-label",
                                style={
                                    "fontSize": "1.1rem",
                                    "fontWeight": "600",
                                    "color": "#2F3E46",
                                    "paddingTop": "26px",
                                },
                            ),
                        ],
                    ),
                    dcc.Slider(
                        id="season-slider",
                        min=0,
                        max=initial_season_index,
                        step=None,
                        value=initial_season_index,
                        marks={index: season for index, season in enumerate(SEASONS)},
                    ),
                ],
            ),
            dcc.Interval(
                id="season-interval",
                interval=SETTINGS.dashboard_interval_ms,
                n_intervals=0,
                disabled=True,
            ),
            dcc.Store(id="is-playing", data=False),
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))",
                    "gap": "16px",
                },
                children=[
                    dcc.Graph(id="history-chart"),
                    dcc.Graph(id="leaderboard-chart"),
                ],
            ),
        ],
    )

    @app.callback(
        Output("is-playing", "data"),
        Output("season-interval", "disabled"),
        Output("play-button", "children"),
        Input("play-button", "n_clicks"),
        State("is-playing", "data"),
    )
    def toggle_playback(n_clicks: int, is_playing: bool) -> tuple[bool, bool, str]:
        if not n_clicks:
            return False, True, "Play"

        next_state = not is_playing
        return next_state, not next_state, "Pause" if next_state else "Play"

    @app.callback(
        Output("season-slider", "value"),
        Input("season-interval", "n_intervals"),
        State("season-slider", "value"),
        prevent_initial_call=True,
    )
    def advance_season(_: int, slider_value: int) -> int:
        if not SEASONS:
            return 0
        if slider_value >= len(SEASONS) - 1:
            return 0
        return slider_value + 1

    @app.callback(
        Output("history-chart", "figure"),
        Output("leaderboard-chart", "figure"),
        Output("season-label", "children"),
        Input("player-select", "value"),
        Input("season-slider", "value"),
    )
    def update_figures(
        selected_ids: list[int] | None, slider_value: int
    ) -> tuple[go.Figure, go.Figure, str]:
        if not SEASONS:
            empty_figure = go.Figure()
            return empty_figure, empty_figure, "Current season: unavailable"

        active_ids = selected_ids or DEFAULT_PLAYER_IDS
        active_season = SEASONS[slider_value]
        history_figure = build_history_figure(active_ids, active_season)
        leaderboard_figure = build_leaderboard_figure(active_ids, active_season)
        return history_figure, leaderboard_figure, f"Current season: {active_season}"

    return app


def run() -> None:
    app = create_app()
    app.run(host=SETTINGS.dashboard_host, port=SETTINGS.dashboard_port, debug=True)


if __name__ == "__main__":
    run()
