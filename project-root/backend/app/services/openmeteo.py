import asyncio
import httpx
from datetime import datetime
from ..core.config import OPEN_METEO_ARCHIVE_URL


async def get_temperature_async(latitude, longitude, target_datetime: datetime):
    """
    Pobiera dane pogodowe i zwraca tylko te dla konkretnej godziny.
    target_datetime: obiekt datetime, np. datetime(2024, 5, 20, 15, 0)
    """

    date_str = target_datetime.strftime("%Y-%m-%d")
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": date_str,
        "end_date": date_str,
        "hourly": "temperature_2m",
        "timezone": "auto"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(OPEN_METEO_ARCHIVE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            if "hourly" not in data:
                return None

            target_iso = target_datetime.strftime("%Y-%m-%dT%H:00")
            
            try:
                idx = data["hourly"]["time"].index(target_iso)

                return {
                    "time": data["hourly"]["time"][idx],
                    "temp": data["hourly"]["temperature_2m"][idx]
                }
            except ValueError:
                print("Nie znaleziono podanej godziny w danych.")
                return None

        except Exception as e:
            print(f"Błąd pogody: {e}")
            return None

async def main():
    # Przykład użycia dla Warszawy (52.2297, 21.0122)
    lat, lon = 52.2297, 21.0122
    day = datetime(2023, 6, 15, 14, 0)

    print(f"Pobieranie pogody dla: {lat}, {lon}...")
    
    temp = await get_temperature_async(lat, lon, day)
    
    if temp is not None:
        print(f"Czas: {temp['time']} | Temp: {temp['temp']}°C")

if __name__ == "__main__":
    asyncio.run(main())