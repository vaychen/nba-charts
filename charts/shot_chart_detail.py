from nba_api.stats.endpoints.shotchartdetail import ShotChartDetail
import requests
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Example: James Harden, 2014-15 Regular Season, all teams (team_id=0)
shot_chart = ShotChartDetail(
    team_id=0,
    player_id=201935,
    season_nullable="2014-15",
    season_type_all_star="Regular Season"
)

# Access shot chart data
shot_df = shot_chart.shot_chart_detail.get_data_frame()
print(shot_df.head())

# # draw a basketball court with matplotlib
sns.set_style("white")
sns.set_color_codes()
plt.figure(figsize=(12, 11))
plt.scatter(shot_df.LOC_X, shot_df.LOC_Y)
plt.show()
