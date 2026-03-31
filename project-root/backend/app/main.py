'''
Uruchamianie za pomocą dockera:

1. Za pierwszym razem:
    docker compose up --build
2. Przy kolejnych uruchomieniach:
    docker compose up
3. Zmieniłeś kod backendu / requirements.txt i chcesz zbudować obraz ponownie:
    docker compose up --build bakcend
'''


from typing import Tuple
from fastapi import FastAPI
from .services.osrm import calculate_with_given_coordinates
from pydantic import BaseModel
from .core.routing_algorithm import solve
import asyncio

class RouteRequest(BaseModel):
    start: Tuple[float, float]
    end: Tuple[float, float]


app = FastAPI()

@app.get("/test")
async def read_root():
    return {"message": "Backend działa"}

@app.post("/calculate_distance")
async def calculate_distance(data: RouteRequest):
    chargings, distance, time, coordinates = await solve(data.start, data.end)
    return {
        "chargings": chargings,
        "distance": distance,
        "time": time,
        "coordinates": coordinates
    }