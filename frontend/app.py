import streamlit as st
import requests
from streamlit_echarts import st_echarts

st.title("NBA Shot Chart Viewer")

player_id = st.number_input("Player ID", min_value=0, value=201935)
season = st.text_input("Season (e.g. 2014-15)", value="2014-15")

if st.button("Get Shot Chart Image"):
    params = {"player_id": player_id, "season": season}
    try:
        image_url = f"http://localhost:8000/shot_chart/image?player_id={player_id}&season={season}"
        st.image(image_url, caption="Shot Chart", use_column_width=True)
    except Exception as e:
        st.error(f"Error fetching shot chart: {e}")

if st.button("Get ECharts Report"):
    try:
        api_url = f"http://localhost:8000/shot_chart?player_id={player_id}&season={season}"
        resp = requests.get(api_url)
        resp.raise_for_status()
        data = resp.json()["data"]
        points = [[d["LOC_X"], d["LOC_Y"]] for d in data]
        option = {
            "title": {"text": "NBA Shot Chart (ECharts)"},
            "tooltip": {},
            "xAxis": {"min": -250, "max": 250},
            "yAxis": {"min": -50, "max": 420},
            "series": [
                {
                    "symbolSize": 6,
                    "data": points,
                    "type": "scatter"
                }
            ]
        }
        st_echarts(options=option, height="600px")
    except Exception as e:
        st.error(f"Error fetching ECharts data: {e}")