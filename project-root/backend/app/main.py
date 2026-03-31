'''
Uruchamianie za pomocą dockera:

1. Za pierwszym razem:
    docker compose up --build
2. Przy kolejnych uruchomieniach:
    docker compose up
3. Zmieniłeś kod / requirements.txt i chcesz zbudować obraz ponownie:
    docker compose up --build
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
def read_root():
    return {"message": "Backend działa"}

@app.post("/calculate_distance")
def calculate_distance(data: RouteRequest):
    response = dict()
    result = asyncio.run(solve(data.start, data.end))
    response["chargings"] = result[0]
    response["distance"] = result[1]
    response["time"] = result[2]
    response["coordinates"] = result[3]
    return response
