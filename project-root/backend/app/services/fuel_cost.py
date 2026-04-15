import os
import httpx


async def get_electricity_price(lat: float, lon: float) -> float:
    api_key = os.getenv("VITE_ELECTRICITY_MAPS_API_KEY")

    if not api_key:
        raise ValueError("Brak klucza VITE_ELECTRICITY_MAPS_API_KEY")

    url = (
        "https://api.electricitymaps.com/v3/price-day-ahead/latest"
        f"?lat={lat}&lon={lon}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers={"auth-token": api_key})

    if response.status_code != 200:
        raise Exception(f"Błąd API prądu: {response.status_code}")

    data = response.json()

    # EUR/MWh → EUR/kWh
    return data["value"] / 1000


async def get_mean_electricity_price(waypoints) -> float:
    price = 0
    for waypoint in waypoints:
        lon, lat = waypoint
        price += await get_electricity_price(lat, lon)

    return price / len(waypoints)


async def calculate_electricity_cost(waypoints, avg_consumption) -> float:
    price = await get_mean_electricity_price(waypoints)
    return price * avg_consumption
