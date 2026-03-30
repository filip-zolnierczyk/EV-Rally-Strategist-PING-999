from typing import Tuple
from fastapi import FastAPI
from services.osrm import calculate_with_given_coordinates
from pydantic import BaseModel
from core.routing_algorithm import solve
import asyncio

class RouteRequest(BaseModel):
    start: Tuple[float, float]
    end: Tuple[float, float]


app = FastAPI()

@app.get("/test")
def read_root():
    return {"message": "Backend działa"}

@app.post("/calculate_distance")
def calculate_distance(data: RouteRequest):
    resposne = dict()
    result = asyncio.run(solve(data.start, data.end))
    resposne["chargings"] = result[0]
    resposne["distance"] = result[1]
    resposne["time"] = result[2]
    resposne["coordinates"] = result[3]
    return resposne
