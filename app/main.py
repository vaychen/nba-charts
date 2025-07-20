from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    Placeholder endpoint for shot chart data.
    """
    return {"player_id": player_id, "season": season, "data": "This will be shot chart data."} 