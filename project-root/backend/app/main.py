from fastapi import FastAPI
from services.osrm import calculate_with_given_coordinates
from sample_chargers_db import sample_chargers
from pydantic import BaseModel

class RouteRequest(BaseModel):
    start: str
    end: str


app = FastAPI()

@app.get("/test")
def read_root():
    return {"message": "Backend działa"}

@app.post("/calculate_distance")
def calculate_distance(data: RouteRequest):
    start = str(data.start)
    end = str(data.end)
    chargers = sample_chargers
    return calculate_with_given_coordinates(start, end, chargers)
