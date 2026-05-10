from pathlib import Path
import json

def get_selected_cars(min_price, max_price, range, body_type, seats):
    data_path = Path(__file__).resolve().parent.parent / "data" / "extra-ev-data.json"

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        cars = data['vehicles']
        filtered_cars = []
        for car in cars:
            try:
                price = car["pricing"]['msrp'][0]['amount']
            except:
                price = 1 #niektóre nie mają ceny wpisanej 

            if (max_price >= price >= min_price) or (min_price == -1):
                    car_body = car["body"]["style"].lower()
                    if (body_type == "any") or (car_body == body_type.lower()):
                        car_seats = car["body"]["seats"]
                        if (seats == -1) or (car_seats == seats):
                            car_range = car["range"]["rated"][0]["range_km"]
                            if range <= car_range:
                                filtered_cars.append({
                                "make": car["make"]["name"],
                                "model": car["model"]["name"],
                                "price": price,
                                "range_km": car_range,
                                "body_type": car_body,
                                "seats": car_seats,
                                "url": car["sources"][0]["url"]
                            })    

    return filtered_cars

print(get_selected_cars(-1, -1, -1, "any", -1))


