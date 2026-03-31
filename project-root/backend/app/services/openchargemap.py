import asyncio
import httpx
from ..core.config import OPENCHARGEMAP_API_KEY, OPENCHARGEMAP_URL
import json
from pathlib import Path

def transform_charger_data(raw_station):

    status = raw_station.get("StatusType", {}).get("Title", "Unknown")
    if status != "Operational":
        return {} 

    address_info = raw_station.get("AddressInfo", {})
    
    connections = []
    for conn in raw_station.get("Connections", []):
        connections.append({
            "plug": conn.get("ConnectionType", {}).get("Title", "Unknown"),
            "plug_id": conn.get("ConnectionTypeID","Unknown"),
            "power_kw": conn.get("PowerKW"),
            "amps": conn.get("Amps"),
            "voltage": conn.get("Voltage")
        })

    return {
        "name": address_info.get("Title"),
        "lat_lon": [address_info.get("Latitude"), address_info.get("Longitude")],
        "address": address_info.get("AddressLine1"),
        "connectors": connections
    }

async def get_charging_stations_async(latitude, longitude, distance):
  
    params = {
        'output': 'json',
        'latitude': latitude,
        'longitude': longitude,
        'distance': distance,
        'distanceunit': 'KM',
        'key': OPENCHARGEMAP_API_KEY
    }
    
    headers = {
        'User-Agent': 'EV-Rally Strategist'
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(OPENCHARGEMAP_URL, params=params, headers=headers, follow_redirects=True)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e}")
            return None

async def get_charging_stations_async_max_result(latitude, longitude, maxresults=5, distance=100):
    params = {
        'output': 'json',
        'latitude': latitude,
        'longitude': longitude,
        'distance': distance,        # 100 km radius
        'distanceunit': 'KM',
        'maxresults': maxresults,    # limit number of returned stations
        'key': OPENCHARGEMAP_API_KEY
    }

    headers = {
        'User-Agent': 'EV-Rally Strategist'
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(OPENCHARGEMAP_URL, params=params, headers=headers, follow_redirects=True)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e}")
            return None
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            return None

async def get_charging_stations_async_max_result_(latitude, longitude):
    stations = await get_charging_stations_async_max_result(latitude, longitude, maxresults=5, distance=100)

    current_file = Path(__file__)
    stations_path = current_file.parent.parent.parent / "stations.json"
    with open(stations_path, 'w', encoding='utf-8') as f:
        json.dump([transform_charger_data(station) for station in stations], f, indent=4, ensure_ascii=False)


async def main():
    stations = await get_charging_stations_async(52.2297, 21.0122, 10)

    import json


    with open('stations.json', 'w', encoding='utf-8') as f:
        json.dump([transform_charger_data(station) for station in stations], f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    asyncio.run(main())