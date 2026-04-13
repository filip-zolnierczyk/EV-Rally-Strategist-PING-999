import json
from pathlib import Path

# Słownik mapowania: Plug_ID z OpenChargeMap -> Klucze w Open-EV-Data
# Uwzględniamy podział na AC (prąd zmienny) i DC (prąd stały)
PLUG_MAPPING = {
    # AC - Prąd zmienny
    25: {"type": "ac", "key": "type2"},      # Type 2 (Socket Only)
    1036: {"type": "ac", "key": "type2"},    # Type 2 (Tethered Connector)
    28: {"type": "ac", "key": "schuko"},     # CEE 7/4 - Schuko - Type F
    30: {"type": "ac", "key": "tesla"},      # Tesla (Model S/X) - zazwyczaj Type 2 modyfikowany
    1: {"type": "ac", "key": "type1"},       # Type 1 (J1772)

    # DC - Prąd stały (Szybkie ładowanie)
    33: {"type": "dc", "key": "ccs"},        # CCS (Type 2)
    2: {"type": "dc", "key": "chademo"},     # CHAdeMO
    27: {"type": "dc", "key": "tesla"},      # Tesla Supercharger
}

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
            return True, "AC"
    
    elif conn_type == "dc":
        supported_ports = vehicle.get("dc_charger", {}).get("ports", [])
        if target_key in supported_ports:
            return True, "DC"

    return False, ""


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