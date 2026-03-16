import io
import matplotlib.pyplot as plt
import seaborn as sns
from nba_api.stats.endpoints.shotchartdetail import ShotChartDetail
from fastapi.responses import StreamingResponse

def generate_shot_chart_image(player_id: int, season: str):
    shot_chart = ShotChartDetail(
        team_id=0,
        player_id=player_id,
        season_nullable=season,
        season_type_all_star="Regular Season"
    )
    shot_df = shot_chart.shot_chart_detail.get_data_frame()

    # draw a basketball court with matplotlib
    sns.set_style("white")
    sns.set_color_codes()
    fig, ax = plt.subplots(figsize=(12, 11))
    ax.scatter(shot_df.LOC_X, shot_df.LOC_Y)
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf

def get_shot_chart_data(player_id: int, season: str):
    shot_chart = ShotChartDetail(
        team_id=0,
        player_id=player_id,
        season_nullable=season,
        season_type_all_star="Regular Season"
    )
    shot_df = shot_chart.shot_chart_detail.get_data_frame()
    # Only keep relevant columns for ECharts (e.g., LOC_X, LOC_Y, ACTION_TYPE, SHOT_MADE_FLAG)
    return shot_df[['LOC_X', 'LOC_Y', 'ACTION_TYPE', 'SHOT_MADE_FLAG']].to_dict(orient='records')
