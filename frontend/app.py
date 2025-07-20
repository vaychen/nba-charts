import streamlit as st
import requests

st.title("NBA Shot Chart Viewer")

player_id = st.number_input("Player ID", min_value=0, value=201935)
season = st.text_input("Season (e.g. 2014-15)", value="2014-15")

if st.button("Get Shot Chart"):
    params = {"player_id": player_id, "season": season}
    try:
        response = requests.get("http://localhost:8000/shot_chart", params=params)
        data = response.json()
        st.write(data)
    except Exception as e:
        st.error(f"Error fetching shot chart: {e}") 