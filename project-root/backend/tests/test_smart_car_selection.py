import json
import pytest

from app.services.smart_car_selection import get_selected_cars


@pytest.fixture
def sample_data(tmp_path, monkeypatch):
    data = {
        "vehicles": [
            {
                "make": {"name": "Tesla"},
                "model": {"name": "Model 3"},
                "pricing": {
                    "msrp": [
                        {"amount": 45000}
                    ]
                },
                "body": {
                    "style": "Sedan",
                    "seats": 5
                },
                "range": {
                    "rated": [
                        {"range_km": 500}
                    ]
                },
                "sources": [
                    {"url": "https://tesla.com/model3"}
                ]
            },
            {
                "make": {"name": "Hyundai"},
                "model": {"name": "Kona"},
                "pricing": {
                    "msrp": [
                        {"amount": 35000}
                    ]
                },
                "body": {
                    "style": "SUV",
                    "seats": 5
                },
                "range": {
                    "rated": [
                        {"range_km": 420}
                    ]
                },
                "sources": [
                    {"url": "https://hyundai.com/kona"}
                ]
            },
            {
                # brak ceny
                "make": {"name": "Unknown"},
                "model": {"name": "NoPrice"},
                "body": {
                    "style": "Sedan",
                    "seats": 4
                },
                "range": {
                    "rated": [
                        {"range_km": 300}
                    ]
                },
                "sources": [
                    {"url": "https://example.com"}
                ]
            }
        ]
    }

    data_dir = tmp_path.parent / "data"
    data_dir.mkdir(exist_ok=True)

    file_path = data_dir / "extra-ev-data.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    import app.services.smart_car_selection as scs

    monkeypatch.setattr(
        scs.Path,
        "resolve",
        lambda self: tmp_path / "fake.py"
    )

    return data


def test_filter_by_price(sample_data):
    result = get_selected_cars(
        min_price=40000,
        max_price=50000,
        range=0,
        body_type="any",
        seats=-1
    )

    assert len(result) == 1
    assert result[0]["make"] == "Tesla"


def test_filter_by_body_type(sample_data):
    result = get_selected_cars(
        min_price=0,
        max_price=100000,
        range=0,
        body_type="SUV",
        seats=-1
    )

    assert len(result) == 1
    assert result[0]["make"] == "Hyundai"


def test_filter_by_seats(sample_data):
    result = get_selected_cars(
        min_price=0,
        max_price=100000,
        range=0,
        body_type="any",
        seats=4
    )

    # auto bez ceny nie powinno przejść
    assert len(result) == 0


def test_filter_by_range(sample_data):
    result = get_selected_cars(
        min_price=0,
        max_price=100000,
        range=450,
        body_type="any",
        seats=-1
    )

    assert len(result) == 1
    assert result[0]["make"] == "Tesla"


def test_any_body_type_returns_multiple(sample_data):
    result = get_selected_cars(
        min_price=0,
        max_price=100000,
        range=0,
        body_type="any",
        seats=-1
    )

    assert len(result) == 2


def test_max_price_minus_one_returns_all_prices(sample_data):
    result = get_selected_cars(
        min_price=999999,
        max_price=-1,
        range=0,
        body_type="any",
        seats=-1
    )

    assert len(result) == 2


def test_car_without_price_is_skipped(sample_data):
    result = get_selected_cars(
        min_price=0,
        max_price=100000,
        range=0,
        body_type="any",
        seats=-1
    )

    models = [car["model"] for car in result]

    assert "NoPrice" not in models


def test_return_structure(sample_data):
    result = get_selected_cars(
        min_price=0,
        max_price=100000,
        range=0,
        body_type="any",
        seats=-1
    )

    car = result[0]

    assert "make" in car
    assert "model" in car
    assert "price" in car
    assert "range_km" in car
    assert "body_type" in car
    assert "seats" in car
    assert "url" in car