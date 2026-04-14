from typing import List, Tuple
from ..services.osrm import *
from ..services.openchargemap import *
from math import inf
import asyncio

RANGE = 400


async def solve(start_point : Tuple[float, float], end_point : Tuple[float, float], carId: str):
    chargings = []

    dist, time, coordinates = calculate_route([start_point, end_point])

    while dist >= RANGE * 0.8:
        # 25%-15% range
        # a_lon, a_lat = coordinates[int(((RANGE*0.8)/dist * len(coordinates))*0.75)]
        b_lon, b_lat = coordinates[int(((RANGE*0.8)/dist * len(coordinates))*0.80)]
        c_lon, c_lat = coordinates[int(((RANGE*0.8)/dist * len(coordinates))*0.85)]
        chargers = []
        # stations = asyncio.run(get_charging_stations_async_max_result_(a_lat, a_lon))
        # chargers += [s["lat_lon"] for s in stations]
        stations = await get_charging_stations_async_max_result_(b_lat, b_lon)
        chargers += [s["lat_lon"] for s in stations if "lat_lon" in s]
        stations = await get_charging_stations_async_max_result_(c_lat, c_lon)
        chargers += [s["lat_lon"] for s in stations if "lat_lon" in s]
        chargers = list(map(convert_to_lonlat, chargers))
        min_time = inf
        min_d = 0
        charging_cords = None
        for charger in chargers:
            d, t, _ = calculate_route([start_point] + chargings + [charger] + [end_point])
            if t < min_time:
                min_time = t
                min_d = d
                charging_cords = charger

        if min_time < inf:
            dist -= min_d
            chargings.append(charging_cords)
            dist, time, coordinates = calculate_route([chargings[-1]] + [end_point])

    dist, time , coordinates = calculate_route([start_point] + chargings + [end_point])
    return chargings, dist, time, coordinates


if __name__ == '__main__':
    start = (19.9450,50.0647)
    end = (21.0122,52.2297)
    result = asyncio.run(solve(start, end))
    print(result[:-1]) # without the exact coordinates of the route








