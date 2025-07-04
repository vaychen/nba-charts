from nba_api.stats.endpoints import playergamelog

game_log_bron = playergamelog.PlayerGameLog(player_id="2544", season="2004")

game_log_bron_df = game_log_bron.get_data_frames()[0]
print(game_log_bron_df.head())
"""
[   SEASON_ID  Player_ID     Game_ID  ... PTS PLUS_MINUS VIDEO_AVAILABLE
0      22004       2544  0020401218  ...  27          9               0
1      22004       2544  0020401209  ...  32         13               0
2      22004       2544  0020401194  ...  37         -6               0
3      22004       2544  0020401174  ...  38         -8               0
4      22004       2544  0020401171  ...  27          1               0
..       ...        ...         ...  ...  ..        ...             ...
75     22004       2544  0020400063  ...  38         14               0
76     22004       2544  0020400051  ...  25         14               0
77     22004       2544  0020400037  ...  31        -12               0
78     22004       2544  0020400018  ...  21         -8               0
79     22004       2544  0020400006  ...  28        -10               0
"""
