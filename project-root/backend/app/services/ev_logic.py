import json
from pathlib import Path
from typing import Optional

# Słownik mapowania: Plug_ID z OpenChargeMap -> Klucze w Open-EV-Data
# Uwzględniamy podział na AC (prąd zmienny) i DC (prąd stały)
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


def get_car_range_and_battery_capacity(carid):
    with open("app/data/ev-data.json", "r", encoding="utf-8") as f:
        vehicles = json.load(f)
    for vehicle in vehicles:
        if vehicle.get("id") == carid:
            battery_size, average_consumption = vehicle.get("usable_battery_size"), vehicle.get("energy_consumption", {}).get("average_consumption")
            return battery_size / average_consumption * 100, battery_size, vehicle  # przeliczamy na km, zakładając że average_consumption jest w kWh/100km

def can_vehicle_charge_with_connector(vehicle, connector):
    """
    Funkcja przyjmuje dane samochodu i dane ładowarki (dokładnie, pojedynczy connector z parametru connectors) i sprawdza, czy są kompatybilne.
    """
    plug_id = connector.get("plug_id")
    
    # 1. Sprawdź czy mamy ten typ wtyczki w słowniku
    mapping = PLUG_MAPPING.get(plug_id)
    if not mapping:
        return False, "Nieznany typ wtyczki"

    target_key = mapping["key"]
    conn_type = mapping["type"] # 'ac' lub 'dc'

    accepted_ports_list = []

    # 2. Sprawdź kompatybilność w odpowiedniej sekcji auta
    if conn_type == "ac":
        supported_ports = vehicle.get("ac_charger", {}).get("ports", [])
            
        if target_key in supported_ports or target_key == "schuko": 
            # Schuko traktujemy jako 'zawsze kompatybilne' jeśli auto ma AC
            return True, plug_id
    
    elif conn_type == "dc":
        supported_ports = vehicle.get("dc_charger", {}).get("ports", [])
        if target_key in supported_ports:
            return True, plug_id

    return False, plug_id

def calculate_range(curr_range : float, temperature : Optional) -> float:
    if temperature is None:
        # może się zdarzyć żę temperatura będzie None
        return curr_range

    optimal_temp = 20.0  # best efficiency around 20°C

    # how strongly temperature affects range
    penalty = 0.02

    delta = abs(temperature['temp'] - optimal_temp)

    # linear degradation
    factor = 1.0 - penalty * delta

    # clamp to avoid unrealistic values
    if factor < 0.6:
        factor = 0.6
    if factor > 1.05:
        factor = 1.05

    return curr_range * factor

def calculate_charging_time(
        battery_capacity: float,
        plug_id: int,
        start_value:float=0.15,
        goal_value:float=0.8
) -> float:
    if PLUG_MAPPING.get(plug_id) is None:
        raise Exception(f"Plug id {plug_id} is not supported")

    if PLUG_MAPPING[plug_id]["type"] == "ac":
        return calculate_charging_time_ac(battery_capacity, PLUG_MAPPING[plug_id]['charger_power_kw'], start_value, goal_value)
    elif PLUG_MAPPING[plug_id]["type"] == "dc":
        return calculate_charging_time_dc(battery_capacity, PLUG_MAPPING[plug_id]['charger_power_kw'], start_value, goal_value)

    raise Exception(f"Plug id {plug_id} is not supported")


def calculate_charging_time_ac(
        battery_capacity: float,
        charger_param: float = 11.0,
        start_value:float=0.15,
        goal_value:float=0.8
) -> float:
    """
    Estimate AC charging time in minutes.
    """

    print(f"DEBUG ------------------ {start_value} -- {goal_value}")
    # if not (0 <= start_value < goal_value <= 1):
    #     raise ValueError("start_value and goal_value must be in [0,1] and start < goal")

    # Tu jest problem bo nie do końca sprawdzane jest czy do ładowarki da się dojechać - problem jest bo star_value jest ujemne wtedy xD
    # To na chwilę TODO
    start_value = max(start_value, 0.0)


    fast_end = min(goal_value, 0.8)

    fast_energy = battery_capacity * max(0.0, fast_end - start_value)
    slow_energy = battery_capacity * max(0.0, goal_value - 0.8)

    fast_time = fast_energy / charger_param
    slow_time = slow_energy / (charger_param * 0.5)  # slower phase

    return fast_time + slow_time

def calculate_charging_time_dc(
    battery_capacity: float,
    charger_power_kw: float,
    start_value: float = 0.10,
    goal_value: float = 0.80,
    vehicle_max_dc_kw: float = 170.0,
) -> float:
    """
    Estimate DC charging time in minutes.
    """

    if battery_capacity <= 0:
        raise ValueError("battery_capacity must be > 0")
    if charger_power_kw <= 0:
        raise ValueError("charger_power_kw must be > 0")
    if vehicle_max_dc_kw <= 0:
        raise ValueError("vehicle_max_dc_kw must be > 0")
    if not (0 <= start_value < goal_value <= 1):
        raise ValueError("start_value and goal_value must be in [0,1] and start < goal")

    available_power = min(charger_power_kw, vehicle_max_dc_kw)

    # (soc_start, soc_end, power_multiplier)
    bands = [
        (0.00, 0.20, 0.90),
        (0.20, 0.40, 0.85),
        (0.40, 0.60, 0.70),
        (0.60, 0.80, 0.55),
        (0.80, 0.90, 0.35),
        (0.90, 1.00, 0.20),
    ]

    total_minutes = 0.0

    for band_start, band_end, multiplier in bands:
        overlap_start = max(start_value, band_start)
        overlap_end = min(goal_value, band_end)

        if overlap_end <= overlap_start:
            continue

        energy_kwh = battery_capacity * (overlap_end - overlap_start)
        effective_power_kw = available_power * multiplier

        # hours = kWh / kW  -> minutes = hours * 60
        total_minutes += (energy_kwh / effective_power_kw) * 60

    return total_minutes


def can_vehicle_charge_with_connector(vehicle, connector):
    """
    Funkcja przyjmuje 
    """
    plug_id = connector.get("plug_id")
    
    # 1. Sprawdź czy mamy ten typ wtyczki w słowniku
    mapping = PLUG_MAPPING.get(plug_id)
    if not mapping:
        return False, "Nieznany typ wtyczki"

    target_key = mapping["key"]
    conn_type = mapping["type"] # 'ac' lub 'dc'

    # 2. Sprawdź kompatybilność w odpowiedniej sekcji auta
    if conn_type == "ac":
        supported_ports = vehicle.get("ac_charger", {}).get("ports", [])
        if target_key in supported_ports or target_key == "schuko": 
            # Schuko traktujemy jako 'zawsze kompatybilne' jeśli auto ma AC
            return True, "AC"
    
    elif conn_type == "dc":
        supported_ports = vehicle.get("dc_charger", {}).get("ports", [])
        if target_key in supported_ports:
            return True, "DC"

    return False, ""


async def get_cars():
    dir = Path(__file__).parent.parent

    with open(dir / "data/ev-data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    return [{
                "id": vehicle_data.get("id"),
                "brand": vehicle_data.get("brand"),
                "model": vehicle_data.get("model"),
                "release_year": vehicle_data.get("release_year"),
                "battery_capacity": vehicle_data.get("usable_battery_size"),
                "avg_consumption": vehicle_data.get("energy_consumption", {}).get("average_consumption")
            } for vehicle_data in data]


def main():
    with open("app/data/ev-data.json", "r", encoding="utf-8") as f:
        vehicles = json.load(f)

    with open("stations.json", "r", encoding="utf-8") as f:
        stations = json.load(f)

    # Przykładowe dane samochodu
    vehicle = vehicles[0]


    # Przykładowy connector z OpenChargeMap
    connector = stations[0].get("connectors", [])[0]  # Pobieramy pierwszy connector z pierwszej stacji

    compatible, conn_type = can_vehicle_charge_with_connector(vehicle, connector)
    if compatible:
        print(f"Samochód jest kompatybilny z tym konektorem ({conn_type}).")
    else:
        print("Samochód NIE jest kompatybilny z tym konektorem.")


    print(get_cars())

if __name__ == "__main__":
    main()