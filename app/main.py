from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from app.services.nba import generate_shot_chart_image, get_shot_chart_data

app = FastAPI(title="NBA Shot Chart API")

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/shot_chart")
def get_shot_chart(player_id: int, season: str):
    """
    Returns shot chart data for a player and season.
    """
    data = get_shot_chart_data(player_id, season)
    return {"player_id": player_id, "season": season, "data": data}


@app.get("/shot_chart/image")
def get_shot_chart_image(player_id: int, season: str):
    buf = generate_shot_chart_image(player_id, season)
    return StreamingResponse(buf, media_type="image/png")
