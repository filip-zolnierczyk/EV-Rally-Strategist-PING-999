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
from fastapi.middleware.cors import CORSMiddleware
from .services.osrm import calculate_with_given_coordinates
from pydantic import BaseModel
from .services.routing_algorithm import solve
from .services.ev_logic import get_cars as get_list_of_cars
import asyncio
import polyline

class RouteRequest(BaseModel):
    start: Tuple[float, float]
    end: Tuple[float, float]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
async def read_root():
    return {"message": "Backend działa"}

@app.post("/calculate_distance")
async def calculate_distance(data: RouteRequest):
    chargings, distance, time, coordinates = await solve(data.start, data.end)

    lat_lng_coords = [(lat, lng) for lng, lat in coordinates]
    encoded_coords = polyline.encode(lat_lng_coords)
    
    return {
        "chargings": chargings,
        "distance": distance,
        "time": time,
        "coordinates": encoded_coords
    }

@app.get("/cars")
async def get_cars():
    return await get_list_of_cars()