from typing import List, Tuple
from .utils import load_stations
from ..services.osrm import *
from ..services.openchargemap import *
from math import inf
import asyncio

def calculate_charging_time(battery_capacity: float, charger_param=0, start_value:float=0.15, goal_value:float=0.8) -> float:
    # TODO
    return 0.0

async def solve(start_point : Tuple[float, float], end_point : Tuple[float, float] , RANGE=600, BATTERY_CAPACITY=1000):
    curr_range = RANGE
    chargings = {"cords" : [], "times" : []}

    dist, time, coordinates, _ = calculate_route([start_point, end_point])

    while dist >= RANGE * 0.8:
        # 25%-15% range
        # a_lon, a_lat = coordinates[int(((RANGE*0.8)/dist * len(coordinates))*0.75)]
        b_lon, b_lat = coordinates[int(((RANGE*0.8)/dist * len(coordinates))*0.80)]
        c_lon, c_lat = coordinates[int(((RANGE*0.8)/dist * len(coordinates))*0.85)]
        chargers = set()
        # stations = asyncio.run(get_charging_stations_async_max_result_(a_lat, a_lon))
        # chargers += set([s["lat_lon"] for s in stations])
        stations = asyncio.run(get_charging_stations_async_max_result_(b_lat, b_lon))
        chargers |= {tuple(s["lat_lon"]) for s in stations}
        stations = asyncio.run(get_charging_stations_async_max_result_(c_lat, c_lon, max_result=3))
        chargers |= {tuple(s["lat_lon"]) for s in stations}
        chargers = list(map(convert_to_lonlat, chargers))
        print(chargers)
        print(len(chargers))
        min_time = inf
        min_d = 0
        charging_cords = None
        best_l = 0
        for charger in chargers:
            d, t, c, l = calculate_route([start_point] + chargings['cords'] + [charger] + [end_point])
            if t < min_time:
                min_time = t
                min_d = d
                charging_cords = charger
                best_l = l[len(chargings['cords'])]['distance'] / 1000


        if min_time < inf:
            dist -= min_d
            chargings['cords'].append(charging_cords)
            dist, time, coordinates, _ = calculate_route([chargings['cords'][-1]] + [end_point])
            curr_range -= best_l
            charging_time = calculate_charging_time(BATTERY_CAPACITY, start_value=curr_range/RANGE)
            chargings['times'].append(charging_time)
            curr_range = RANGE * 0.8

    dist, time , coordinates, _ = calculate_route([start_point] + chargings['cords'] + [end_point])
    return chargings['cords'], dist, time, coordinates


if __name__ == '__main__':
    start = (19.9450,50.0647)
    end = (21.0122,52.2297)
    result = asyncio.run(solve(start, end))
    print(result[:-1]) # without the exact coordinates of the route








