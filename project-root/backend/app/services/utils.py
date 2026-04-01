import json
from pathlib import Path

# not used anymore, deleting soon
def load_stations():
    current_file = Path(__file__)
    stations_path = current_file.parent.parent.parent / "stations.json"

    stations = []
    with open(stations_path, "r") as file:
        data = json.load(file)

    for station in data:
        if station:
            stations.append(station["lat_lon"])

    return stations


if __name__ == "__main__":
    s = load_stations()
    print(s)