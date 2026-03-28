from typing import List, Tuple

from utils import load_stations
from backend.app.services.osrm import *
from backend.app.services.openchargemap import *
from math import inf

RANGE = 300



def solve(start_point : Tuple[float, float], end_point : Tuple[float, float] ):
    chargings = []

    dist, time, coordinates = calculate_route([start_point, end_point])

    print(dist/RANGE)

    while dist >= RANGE * 0.8:
        # 25%-15% range
        # coordinates[(int((RANGE*0.8)/dist * len(coordinates)))*0.75 : (int((RANGE*0.8)/dist * len(coordinates)))*0.85]
        a_lon, a_lat = coordinates[int(((RANGE*0.8)/dist * len(coordinates))*0.75)]
        b_lon, b_lat = coordinates[int(((RANGE*0.8)/dist * len(coordinates))*0.80)]
        c_lon, c_lat = coordinates[int(((RANGE*0.8)/dist * len(coordinates))*0.85)]
        chargers = []
        get_charging_stations_async_max_result_(a_lat, a_lon)
        chargers += load_stations()
        print(len(chargers))
        get_charging_stations_async_max_result_(b_lat, b_lon)
        chargers += load_stations()
        get_charging_stations_async_max_result_(c_lat, c_lon)
        chargers += load_stations()
        # print(chargers)
        chargers = list(map(convert_to_lonlat, chargers))

        min_time = inf
        min_d = 0
        charging_coords = None
        print("DEBUG",len(chargers))
        for charger in chargers:
            print(charger)
            d, t, _ = calculate_route([start_point] + chargings + [charger] + [end_point])
            if t < min_time:
                min_time = t
                min_d = d
                charging_coords = charger

        if min_time < inf:
            dist -= min_d
            chargings.append(charging_coords)

            dist, time, coordinates = calculate_route([chargings[-1]] + [end_point])




    return chargings, dist, time


if __name__ == '__main__':
    start = (19.9450,50.0647)
    end = (21.0122,52.2297)
    print(solve(start, end))








