'''
Uruchamianie za pomocą dockera:

1. Za pierwszym razem:
    docker compose up --build
2. Przy kolejnych uruchomieniach:
    docker compose up
3. Zmieniłeś kod backendu / requirements.txt i chcesz zbudować obraz ponownie:
    docker compose up --build bakcend
'''


from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .services.routing_algorithm import solve
from .services.ev_logic import get_cars as get_list_of_cars
import asyncio
import polyline

class RouteRequest(BaseModel):
    start: List[float] = Field(
        ..., 
        json_schema_extra={"example": [18.6466, 54.3520]},
        description="Współrzędne startowe (Gdańsk) [lng, lat]"
    )
    end: List[float] = Field(
        ..., 
        json_schema_extra={"example": [14.4378, 50.0755]},
        description="Współrzędne docelowe (Praga) [lng, lat]"
    )
    carId: str = Field(
        ..., 
        json_schema_extra={"example": "c6a6bd26-6a8f-4ab7-baf3-6cfa057044e3"},        
        description="UUID wybranego pojazdu"
    )
    dateTime: str = Field(
        ..., 
        json_schema_extra={"example": "2026-04-14T20:15"},
        description="Data i godzina wyjazdu w formacie ISO (YYYY-MM-DDTHH:mm)"    
    )
    charging_to_100: bool = Field(
        default=False,
        description="Czy ładować do 100% czy do 80%"
    )
    charger_type: str = Field(
        default="all",
        description="Typ preferowanych ładowarek (all, ac, dc)"
    )
    min_charger_power: int = Field(
        default=0,
        description="Minimalna moc ładowarki w kW"
    )
    max_stop_time: int = Field(
        default=480,
        description="Maksymalny czas pojedynczego postoju w minutach"
    )


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
    chargings, distance, time, coordinates, total_time, cost = await solve(data.start, data.end, data.carId, charging_to_100=data.charging_to_100)

    lat_lng_coords = [(lat, lng) for lng, lat in coordinates]
    encoded_coords = polyline.encode(lat_lng_coords)
    
    return {
        "chargings": chargings['cords'],
        "distance": distance,
        "time": time,
        "coordinates": encoded_coords,
        "total_time": total_time,
        "charging_time": chargings['times'],
        "charger_info": chargings['charger_info'],
        "plugs": chargings['plugs'],
        "cost": cost
    }

@app.get("/cars")
async def get_cars():
    return await get_list_of_cars()