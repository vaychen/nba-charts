Dynamic 3-Pointers Made Chart (2000 – Now)
-----------------------------------------

Overview
- Goal: Build a dynamic chart showing 3-pointers made (FG3M) by NBA players from the 2000-01 season to the latest season, with a rolling time view and per-player avatars displayed alongside stats.
- Target audience: Data engineers and BI users who want to explore player-level shooting evolution over time.
- Deliverable: a small, self-contained report/demo in this repo (doc first), plus an optional Dash app or frontend for live exploration.

Assumptions
- Data will be sourced from NBA APIs (clone-ready via nba_api or equivalent) and preprocessed into a time-series per player per season.
- Avatar images for players will be hosted publicly (or bundled in the repo) and referenced by URL in the visualization.
- The initial MVP supports a rolling window across seasons and a play/pause scrub control.

1) Data model and schema
- Time: season_id (string) like "2000-01" or a numeric index for ordering.
- Player: player_id (int), name (string), avatar_url (string).
- Metrics: fg3m (integer) – three-pointers made in that season for the player.
- Dataset shape (long format):
  {
    season_id: "2000-01",
    player_id: 123,
    player_name: "John Doe",
    avatar_url: "https://.../123.png",
    fg3m: 100
  }

2) Data ingestion plan
- Source: per-season player statistics endpoint (e.g., nba_api.stats.endpoints.PlayerCareerStats or equivalent) delivering FG3M per player per season.
- Steps:
  1. Build a master player list: player_id, name, avatar_url (from NBA API or a local mapping).
  2. For each season from 2000-01 to current, fetch FG3M per player.
  3. Normalize season formatting to a consistent key (e.g., "2000-01").
  4. Merge into a single time-series dataset; store as JSON or Parquet for fast loading.
- Notes:
  - Consider batching across seasons to respect API limits.
  - For early seasons with incomplete data, fill FG3M with 0 or NaN and document gaps.

3) Visualization approaches (MVP options)
- Option A: Dash + Plotly (recommended for Python projects)
  - Type: interactive line chart with multiple series (players).
  - Time axis: season_id; animation frame or play/slider to roll through seasons.
  - Avatars: show via hover tooltip using HTML image tag or a side avatar panel; optionally render avatars as markers using customdata.
  - Interaction: select subset of players, pause/play, scrub seasons, tooltips with player, season, and value.

- Option B: Web frontend with ECharts / D3 + a Python API backend
  - Backend: FastAPI or Flask serving the precomputed dataset.
  - Frontend: ECharts line chart with a time slider; avatars shown in a separate panel or as tooltips.
  - Pros: clean separation, flexible UI, easy to host.

- Option C: BI tools (Power BI / Tableau)
  - Pros: fast iteration, governance, shareability.
  - Cons: embedding per-player avatars in tooltips may be non-trivial; real-time streaming may require extra work.

4) MVP implementation sketch (Dash/Plotly)
- Data: load precomputed dataset into memory (e.g., pandas DataFrame with columns: season_id, player_id, player_name, avatar_url, fg3m).
- Layout:
  - Left panel: player selection (multi-select with search); a small avatar grid for quick reference.
  - Right panel: animated line chart showing fg3m over seasons for selected players.
  - Bottom/side: play/pause button, season scrub slider, current season label.

- Core code sketch (Python, Dash):
```
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

df = pd.read_json('data/fg3m_by_season.parquet', lines=True)  # precomputed dataset

app = dash.Dash(__name__)

def build_figure(selected_ids, season=None):
    traces = []
    for pid, group in df[df['player_id'].isin(selected_ids)].groupby('player_id'):
        name = group['player_name'].iloc[0]
        avatar = group['avatar_url'].iloc[0]
        traces.append(go.Scatter(
            x=group['season_id'],
            y=group['fg3m'],
            mode='lines+markers',
            name=name,
            text=group.apply(lambda r: f"<img src='{r.avatar_url}' width='28' height='28'> {r.player_name}", axis=1),
            hovertemplate='%{text}<br>Season: %{x}<br>FG3M: %{y}',
            customdata=group[['avatar_url']].values,
        ))
    fig = go.Figure(data=traces)
    fig.update_layout(
        xaxis={'title': 'Season'},
        yaxis={'title': 'FG3M'},
        hovermode='closest',
        margin={'l': 40, 'r': 10, 't': 30, 'b': 40},
    )
    return fig

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='player-select', multi=True,
            options=[{'label': f"{r['player_name']}", 'value': r['player_id']} for _, r in df.drop_duplicates('player_id').iterrows()],
            value=[df['player_id'].unique()[0]],
            style={'width': '300px'}
        ),
        html.Button('Play', id='play', n_clicks=0)
    ], style={'padding': 10}),
    dcc.Graph(id='fg3m-graph', figure=build_figure([df['player_id'].unique()[0]])),
    dcc.Interval(id='interval', interval=2000, n_intervals=0, disabled=True)
])

@app.callback(
    dash.dependencies.Output('fg3m-graph', 'figure'),
    [dash.dependencies.Input('player-select', 'value'), dash.dependencies.Input('interval', 'n_intervals')]
)
def update_graph(selected_ids, n):
    return build_figure(selected_ids or [], None if not selected_ids else None)

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
```

- Phase 2 tasks:
  - Implement data loader to read from JSON/Parquet and cache in memory.
  - Build UI with controls for players, time window, and play/pause.
  - Add avatar tooltips and optional avatar gallery panel.
  - Add export options (PNG or JSON).

5) Data source integration notes
- NBA data availability: FG3M per season is widely available in nba_api endpoints such as PlayerCareerStats or league sums.
- Avatar URLs: use a stable source (NBA player headshots or Basketball-Reference headshots) and maintain a mapping to player_id.
- Update cadence: for a 3-decades range, precompute and store to avoid runtime heavy API calls.

6) Project milestones and deliverables
- Milestone 1: Data extraction + schema definition (doc, sample dataset under data/).
- Milestone 2: Dash app skeleton with basic interactivity and animation.
- Milestone 3: Avatar rendering in tooltips and an optional avatar gallery.
- Milestone 4: Dockerized deployment scripts and a minimal CI check.

What I need from you
- Confirm preferred MVP path (Dash/Plotly vs. ECharts frontend).
- Confirm whether to fetch data live in this repo (via nba_api) or to rely on precomputed data in data/.
- Any constraints on avatar source licensing or hosting (public URLs only, or local assets allowed).

Next steps
- I will add the doc to the repo as the baseline and then start implementing the MVP according to your chosen path. If you don’t object, I’ll begin with a Dash/Plotly MVP and include a simple local data generator for testing, so you can review the UX quickly.
