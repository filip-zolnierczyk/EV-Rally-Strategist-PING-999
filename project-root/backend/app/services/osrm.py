from typing import List, Tuple
from math import inf

import requests

OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving/"

# lat,lon -> lon,lat
def convert_to_lonlat(position : Tuple[float, float]) -> Tuple[float, float]:
    lat, lon = position
    return (lon, lat)

def coordinates_to_str(coordinates : Tuple[float, float]) -> str:
    lon, lat = coordinates
    return str(lon) + "," + str(lat)

def coordinates_to_tuple(coordinates : str) -> Tuple[float, float]:
    result = "".join(coordinates.split())
    lat, lon = result.split(",")
    return (float(lon), float(lat))

def calculate_distance(start : Tuple[float, float], end : Tuple[float, float]):
    start_s = coordinates_to_str(start)
    end_s = coordinates_to_str(end)
    url = f"{OSRM_BASE_URL}/{start_s};{end_s}"
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

def calculate_route(waypoints : List[Tuple[float, float]]):
    url = f"{OSRM_BASE_URL}"
    for waypoint in waypoints:
        waypoint_s = coordinates_to_str(waypoint)
        url = f"{url}{waypoint_s};"
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

    return distance_km, duration_min, route['geometry']['coordinates']


def optimize_distance_with_charging(start : Tuple[float, float], end : Tuple[float, float], chargers : List[Tuple[float, float]]):
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

    # start = coordinates_to_tuple(start)
    # end = coordinates_to_tuple(end)
    #
    # chargers = ["51.360542, 21.130188", "51.067327 , 20.841432", "51.620237 , 20.974218 "]
    # chargers = list(map(coordinates_to_tuple, chargers))
    # chargers = list(map(convert_to_lonlat, chargers))
    # direct_distance, direct_duration = calculate_distance(start, end)
    # print(f"Direct distance: {direct_distance:.2f} km")
    # print(f"Direct duration: {direct_duration:.2f} minutes")
    # charger_duration, charger_distance, charger_position =optimize_distance_with_charging(start, end, chargers)
    # print(f"Charger distance: {charger_distance:.2f} km")
    # print(f"Charger duration: {charger_duration:.2f} minutes")
    # print(f"Charger position: ({charger_position})")

    url = f"{OSRM_BASE_URL}/{start};{end}"


    params = {
        "overview": "full",
        "geometries": "geojson"
    }
    response = requests.get(url, params=params)
    data = response.json()
    print(data['routes'][0]['geometry']['coordinates'])