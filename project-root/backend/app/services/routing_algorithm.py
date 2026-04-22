from typing import List, Tuple, Optional
from ..services.osrm import *
from ..services.openchargemap import *
from ..services.openmeteo import *
from math import inf
import asyncio
from datetime import datetime, timedelta
from ..services.ev_logic import *
from ..services.fuel_cost import *

PLUG_MAPPING = {
    # AC - Prąd zmienny
    25: {"type": "ac", "key": "type2", "charger_power_kw": 11.0, "plug_name": "Type 2 (Socket Only)"},      # Type 2 (Socket Only)
    1036: {"type": "ac", "key": "type2", "charger_power_kw": 11.0, "plug_name": "Type 2 (Tethered Connector)"},    # Type 2 (Tethered Connector)
    28: {"type": "ac", "key": "schuko", "charger_power_kw": 2.3, "plug_name": "CEE 7/4 - Schuko - Type F"},     # CEE 7/4 - Schuko - Type F
    30: {"type": "ac", "key": "tesla", "charger_power_kw": 11.0, "plug_name": "Tesla (Model S/X)"},      # Tesla (Model S/X) - zazwyczaj Type 2 modyfikowany
    1: {"type": "ac", "key": "type1", "charger_power_kw": 7.4, "plug_name": "Type 1 (J1772)"},       # Type 1 (J1772)

    # DC - Prąd stały (Szybkie ładowanie)
    33: {"type": "dc", "key": "ccs", "charger_power_kw": 150.0, "plug_name": "CCS (Type 2)"},        # CCS (Type 2)
    2: {"type": "dc", "key": "chademo", "charger_power_kw": 50.0, "plug_name": "CHAdeMO"},     # CHAdeMO
    27: {"type": "dc", "key": "tesla", "charger_power_kw": 250.0, "plug_name": "Tesla Supercharger"},      # Tesla Supercharger
}

# Główna funkcja algorytmu wyznaczania trasy z postojami na ładowanie.
# start_point / end_point są w formacie (lon, lat).
# RANGE oznacza nominalny zasięg pojazdu (km), BATTERY_CAPACITY to pojemność baterii (jednostka wg modelu domenowego).
async def solve(
        start_point : Tuple[float, float],
        end_point : Tuple[float, float] ,
        carId: str,
        dateTime=datetime.now(),
        charging_to_100=False #
):
    charging_cap = 1.0 if charging_to_100 else 0.8
    RANGE, BATTERY_CAPACITY, vehicle = get_car_range_and_battery_capacity(carId)

    #Pobranie aktualnego czasu
    now = dateTime - timedelta(days=7) # odejmujemy dzień, aby mieć pewność że pogoda będzie dostępna w archiwum Open Meteo
    print(now)

    # Pobranie bieżącej temperatury dla punktu startowego.
    print(start_point[1], start_point[0], datetime(now.year, now.month, now.day, now.hour, now.minute))
    now = datetime(now.year, now.month, now.day, now.hour, now.minute)
    temperature = await get_temperature_async(start_point[1], start_point[0], now)
    # Wyznaczenie efektywnego zasięgu.
    curr_range = calculate_range(charging_cap * RANGE, temperature)

    # Struktura przechowująca:
    # - 'cords': współrzędne wybranych stacji ładowania
    # - 'times': czasy ładowań dla kolejnych postojów
    chargings = {"cords" : [], "times" : [], "charger_info": [], "plugs": []}

    dist, time, coordinates, _ = calculate_route([start_point, end_point], steps=False)

    # Dopóki dystans jest większy niż aktualny zasięg szukamy kolejnych stacji ładowania.
    while dist >= curr_range:
        # Wyznaczenie punktów w okolicach 80% i 85% odcinka obecnej trasy,
        # aby szukać ładowarek „przed końcem dostępnego zasięgu”.
        b_lon, b_lat = coordinates[int((curr_range/dist * len(coordinates))*0.80)]
        c_lon, c_lat = coordinates[int((curr_range/dist * len(coordinates))*0.85)]

        # Używamy zbioru, aby automatycznie usuwać duplikaty stacji.
        charger_cord_set = []
        candidate_stations = []

        # Pobranie kandydatów stacji dla obu punktów i dodanie ich do wspólnego zbioru.
        stations = await get_charging_stations_async_max_result_(b_lat, b_lon, max_result=3)
        stations += await get_charging_stations_async_max_result_(c_lat, c_lon, max_result=3)
        for station in stations:
            if 'lat_lon' in station and station['lat_lon'] is not None and convert_to_lonlat(tuple(station['lat_lon'])) not in charger_cord_set:
                station['lon_lat'] = convert_to_lonlat(tuple(station['lat_lon']))
                charger_cord_set.append(station['lon_lat'])
                candidate_stations.append(station)

        # Szukamy stacji, która minimalizuje całkowity czas przejazdu po jej dodaniu do trasy.
        min_time = inf
        min_d = 0
        charging_cords = None
        best_l = 0
        best_i = 0
        for i, charger in enumerate(charger_cord_set):
            # Wyznaczenie trasy z dotychczasowymi ładowaniami + nowym kandydatem.
            # l zawiera listę „legs”, dzięki czemu możemy odczytać długość odcinka do aktualnie rozważanej stacji.
            d, t, c, l = calculate_route([start_point] + chargings['cords'] + [charger] + [end_point])
            if t < min_time:
                min_time = t
                min_d = d
                charging_cords = charger
                # Długość odcinka prowadzącego do nowo dodanej stacji (w km).
                best_l = l[len(chargings['cords'])]['distance'] / 1000
                best_i = i
        chargings['charger_info'].append(candidate_stations[best_i])

        # Jeśli znaleźliśmy sensownego kandydata, aktualizujemy stan planu podróży.
        if min_time < inf:
            # Przybliżona aktualizacja pozostałego dystansu.
            dist -= min_d

            # Dodanie wybranej stacji do listy postojów.
            chargings['cords'].append(charging_cords)

            # Przeliczenie pozostałej części trasy: od ostatniej stacji do celu.
            dist, time, coordinates, _ = calculate_route([chargings['cords'][-1]] + [end_point], steps=False)

            # Aktualizacja „stanu baterii” w uproszczonym modelu.
            curr_range -= best_l

            # Wyznaczenie czasu ładowania dla aktualnego postoju.
            best_plug_id = 28
            for connector in candidate_stations[best_i]['connectors']:
                res, plug_id = can_vehicle_charge_with_connector(vehicle, connector)
                if res and PLUG_MAPPING[25]['charger_power_kw'] > PLUG_MAPPING[best_plug_id]['charger_power_kw']:
                    best_plug_id = 28

            charging_time = calculate_charging_time(BATTERY_CAPACITY, plug_id=best_plug_id, start_value=curr_range/RANGE, goal_value=charging_cap)
            chargings['times'].append(charging_time)
            chargings['plugs'].append(PLUG_MAPPING[best_plug_id])

            # Pobranie prognozy temperatury na moment dotarcia do tej stacji
            # i przeliczenie zasięgu po ładowaniu do 80%.
            temperature = await get_temperature_async(charging_cords[1], charging_cords[0], now + timedelta(minutes=min_time))
            curr_range = calculate_range(charging_cap*RANGE, temperature)
        else:
            raise Exception(f"Could not find a charger on the route")

    # Końcowe przeliczenie pełnej trasy ze wszystkimi przystankami.
    dist, time , coordinates, _ = calculate_route([start_point] + chargings['cords'] + [end_point], steps=False)

    # print(f" DEBUG: {chargings['times']}")
    # Zwracamy: listę stacji ładowania, dystans, czas, geometrię trasy, ew czasy każdego ładowania
    total_time = time + sum(chargings['times'])
    if chargings['cords']:
        cost = await calculate_electricity_cost(chargings['cords'], vehicle.get("energy_consumption").get("average_consumption"), dist)
    else:
        cost = await calculate_electricity_cost([start_point], vehicle.get("energy_consumption").get("average_consumption"), dist)
    return chargings, dist, time, coordinates, total_time, cost









