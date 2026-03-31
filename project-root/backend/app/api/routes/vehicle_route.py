from fastapi import APIRouter
from ...models.route import RouteRequest
from app.services.routing_algorithm import solve


router = APIRouter()

@router.post("/vehicle-route")
async def vehicle_route(data: RouteRequest):
    chargings, distance, time, route = await solve(data.start, data.end)
    return {
        "chargings": chargings,
        "distance": distance,
        "time": time,
        "route": route
    }