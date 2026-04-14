from typing import List, Tuple, Optional
from ..services.osrm import *
from ..services.openchargemap import *
from ..services.openmeteo import *
from math import inf
import asyncio
from datetime import datetime, timedelta
from ..services.ev_logic import *


# Główna funkcja algorytmu wyznaczania trasy z postojami na ładowanie.
# start_point / end_point są w formacie (lon, lat).
# RANGE oznacza nominalny zasięg pojazdu (km), BATTERY_CAPACITY to pojemność baterii (jednostka wg modelu domenowego).
async def solve(start_point : Tuple[float, float], end_point : Tuple[float, float] , carId: str):
    RANGE, BATTERY_CAPACITY = 400, 100

    # WZIĄĆ Z            carId
    
    # Pobranie bieżącej temperatury dla punktu startowego.
    temperature = await get_temperature_async(start_point[1], start_point[0], datetime.now())
    # Wyznaczenie efektywnego zasięgu.
    curr_range = calculate_range(RANGE, temperature)

    # Struktura przechowująca:
    # - 'cords': współrzędne wybranych stacji ładowania
    # - 'times': czasy ładowań dla kolejnych postojów
    chargings = {"cords" : [], "times" : []}

    dist, time, coordinates, _ = calculate_route([start_point, end_point], steps=False)

    # Dopóki dystans jest większy niż aktualny zasięg szukamy kolejnych stacji ładowania.
    while dist >= curr_range:
        # Wyznaczenie punktów w okolicach 80% i 85% odcinka obecnej trasy,
        # aby szukać ładowarek „przed końcem dostępnego zasięgu”.
        b_lon, b_lat = coordinates[int(((RANGE*0.8)/dist * len(coordinates))*0.80)]
        c_lon, c_lat = coordinates[int(((RANGE*0.8)/dist * len(coordinates))*0.85)]

        # Używamy zbioru, aby automatycznie usuwać duplikaty stacji.
        charger_cord_set = set()

        # Pobranie kandydatów stacji dla obu punktów i dodanie ich do wspólnego zbioru.
        stations = await get_charging_stations_async_max_result_(b_lat, b_lon, max_result=3)
        charger_cord_set |= {tuple(s["lat_lon"]) for s in stations if 'lat_lon' in s}
        stations = await get_charging_stations_async_max_result_(c_lat, c_lon, max_result=3)
        charger_cord_set |= {tuple(s["lat_lon"]) for s in stations if 'lat_lon' in s}

        # Konwersja współrzędnych do oczekiwanego formatu (lon, lat).
        charger_cord_set = list(map(convert_to_lonlat, charger_cord_set))

        # Szukamy stacji, która minimalizuje całkowity czas przejazdu po jej dodaniu do trasy.
        min_time = inf
        min_d = 0
        charging_cords = None
        best_l = 0
        for charger in charger_cord_set:
            # Wyznaczenie trasy z dotychczasowymi ładowaniami + nowym kandydatem.
            # l zawiera listę „legs”, dzięki czemu możemy odczytać długość odcinka do aktualnie rozważanej stacji.
            d, t, c, l = calculate_route([start_point] + chargings['cords'] + [charger] + [end_point])
            if t < min_time:
                min_time = t
                min_d = d
                charging_cords = charger
                # Długość odcinka prowadzącego do nowo dodanej stacji (w km).
                best_l = l[len(chargings['cords'])]['distance'] / 1000

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
            charging_time = calculate_charging_time(BATTERY_CAPACITY, plug_id=2, start_value=curr_range/RANGE)
            chargings['times'].append(charging_time)

            # Pobranie prognozy temperatury na moment dotarcia do tej stacji
            # i przeliczenie zasięgu po ładowaniu do 80%.
            temperature = await get_temperature_async(charging_cords[1], charging_cords[0], datetime.now() + timedelta(minutes=min_time))
            curr_range = calculate_range(0.8*RANGE, temperature)
        else:
            raise Exception(f"Could not find a charger on the route")

    # Końcowe przeliczenie pełnej trasy ze wszystkimi przystankami.
    dist, time , coordinates, _ = calculate_route([start_point] + chargings['cords'] + [end_point], steps=False)

    # print(f" DEBUG: {chargings['times']}")
    # Zwracamy: listę stacji ładowania, dystans, czas, geometrię trasy, ew czasy każdego ładowania
    return chargings['cords'], dist, time, coordinates#, chargings['times']


if __name__ == '__main__':
    start = (19.9450,50.0647)
    end = (21.0122,52.2297)
    result = asyncio.run(solve(start, end))
    print(result[:-1]) # without the exact coordinates of the route








