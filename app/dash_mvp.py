import json
import pathlib
import pandas as pd
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

DATA_PATH = pathlib.Path(__file__).parents[1] / 'data' / 'fg3m_by_season_sample.json'

def load_data(path=None):
    path = path or DATA_PATH
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # Ensure types
    df['season_id'] = df['season_id'].astype(str)
    df['player_id'] = df['player_id'].astype(int)
    df['fg3m'] = df['fg3m'].astype(int)
    return df

df = load_data()

player_list = df.groupby(['player_id', 'player_name', 'avatar_url']).size().reset_index().drop(columns=[0])
player_options = [
    {'label': row['player_name'], 'value': int(row['player_id'])}
    for _, row in player_list.iterrows()
]
all_seasons = sorted(df['season_id'].unique())

def build_figure(selected_ids, upto_season):
    traces = []
    sel = df[df['player_id'].astype(int).isin(selected_ids or [])]
    if upto_season:
        sel = sel[sel['season_id'] <= upto_season]

    for pid, grp in sel.groupby('player_id'):
        name = grp['player_name'].iloc[0]
        avatar = grp['avatar_url'].iloc[0]
        # build helper text with avatar image
        grp = grp.copy()
        grp['text'] = grp.apply(lambda r: f"<img src='{r['avatar_url']}' width='22' height='22'> {r['player_name']}", axis=1)
        traces.append(
            go.Scatter(
                x=grp['season_id'],
                y=grp['fg3m'],
                mode='lines+markers',
                name=name,
                hovertemplate='%{text}<br>Season: %{x}<br>FG3M: %{y}<extra></extra>',
                text=grp['text'],
            )
        )
    fig = go.Figure(data=traces)
    fig.update_layout(
        xaxis={'title': 'Season'},
        yaxis={'title': 'FG3M'},
        hovermode='closest',
        margin={'l': 60, 'r': 20, 't': 30, 'b': 40},
        height=520,
    )
    return fig

app = dash.Dash(__name__)
app.layout = html.Div([
    html.Div([
        html.Label('Select players'),
        dcc.Dropdown(
            id='player-select',
            options=player_options,
            value=[player_options[0]['value']] if player_options else [],
            multi=True,
            placeholder='Choose players...'
        ),
        html.Button('Play', id='play', n_clicks=0)
    ], style={'padding': '12px'}),
    dcc.Graph(id='fg3m-graph', figure=build_figure([player_options[0]['value']] if player_options else [], all_seasons[-1] if all_seasons else None)),
    dcc.Slider(
        id='season-slider',
        min=0,
        max=len(all_seasons) - 1,
        value=len(all_seasons) - 1,
        marks={i: season for i, season in enumerate(all_seasons)},
        step=None
    ),
    html.Div(id='season-label', style={'padding': '6px 12px'})
])

@app.callback(
    Output('fg3m-graph', 'figure'),
    [Input('player-select', 'value'), Input('season-slider', 'value')]
)
def update_graph(selected_ids, slider_value):
    upto = all_seasons[slider_value] if slider_value is not None else None
    return build_figure(selected_ids, upto)

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
