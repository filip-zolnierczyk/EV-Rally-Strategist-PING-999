from typing import List
from math import inf

import requests

OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving/"

# lat,lon -> lon,lat
def convert_to_lonlat(position : str) -> str:
    result = "".join(position.split())
    lat, lon = result.split(",")
    return lon + "," + lat

def calculate_distance(start : str, end : str):
    url = f"{OSRM_BASE_URL}/{start};{end}"
    params = {
        "overview": "full",
        "geometries": "geojson"
    }
    response = requests.get(url, params=params)
    data = response.json()

    route = data["routes"][0]

    distance_km = route["distance"] / 1000
    duration_min = route["duration"] / 60

    return distance_km, duration_min

def calculate_route(waypoints : List[str]):
    url = f"{OSRM_BASE_URL}"
    for waypoint in waypoints:
        url = f"{url}{waypoint};"
    url = url[:-1]

    params = {
        "overview": "full",
        "geometries": "geojson"
    }
    response = requests.get(url, params=params)
    data = response.json()
    route = data["routes"][0]

    distance_km = route["distance"] / 1000
    duration_min = route["duration"] / 60

    return distance_km, duration_min


def optimize_distance_with_charging(start : str, end : str, chargers : List[str]):
    # for now testing routing with only one charging, only for api testing, will change it asap
    # optimizing for time, I guess it could be a parameter to optimize time vs distance idk
    current_duration = inf
    current_distance = inf
    current_charger_position = ""
    for charger in chargers:
        distance, duration = calculate_route([start, charger, end])
        if duration < current_duration:
            current_duration = duration
            current_distance = distance
            current_charger_position = charger

    return current_duration, current_distance, current_charger_position


if __name__ == "__main__":
    start = "19.9450,50.0647"
    end = "21.0122,52.2297"

    chargers = ["51.360542, 21.130188", "51.067327 , 20.841432", "51.620237 , 20.974218 "]
    chargers = list(map(convert_to_lonlat, chargers))
    direct_distance, direct_duration = calculate_distance(start, end)
    print(f"Direct distance: {direct_distance:.2f} km")
    print(f"Direct duration: {direct_duration:.2f} minutes")
    charger_duration, charger_distance, charger_position =optimize_distance_with_charging(start, end, chargers)
    print(f"Charger distance: {charger_distance:.2f} km")
    print(f"Charger duration: {charger_duration:.2f} minutes")
    print(f"Charger position: ({charger_position})")