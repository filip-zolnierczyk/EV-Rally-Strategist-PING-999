import pytest
from datetime import datetime

from app.services import routing_algorithm as ra


@pytest.mark.asyncio
async def test_solve_without_charging_needed(monkeypatch):
    vehicle = {
        "id": "car-1",
        "ac_charger": {"ports": ["type2", "schuko"]},
        "dc_charger": {"ports": ["ccs"]},
        "energy_consumption": {"average_consumption": 20},
    }

    monkeypatch.setattr(
        ra,
        "get_car_range_and_battery_capacity",
        lambda car_id: (500, 100, vehicle)
    )

    monkeypatch.setattr(
        ra,
        "get_temperature_async",
        lambda lat, lon, date: async_return({"temp": 20})
    )

    monkeypatch.setattr(
        ra,
        "calculate_route",
        lambda points, steps=False: (300, 180, [(0, 0), (1, 1)], [])
    )

    monkeypatch.setattr(
        ra,
        "calculate_electricity_cost",
        lambda waypoints, avg_consumption, dist: async_return(123.45)
    )

    result = await ra.solve(
        start_point=(0, 0),
        end_point=(1, 1),
        carId="car-1",
        dateTime=datetime(2026, 1, 1, 12, 0)
    )

    chargings, dist, time, coordinates, total_time, cost = result

    assert chargings["cords"] == []
    assert chargings["times"] == []
    assert chargings["charger_info"] == []
    assert chargings["plugs"] == []

    assert dist == 300
    assert time == 180
    assert coordinates == [(0, 0), (1, 1)]
    assert total_time == 180
    assert cost == 123.45


@pytest.mark.asyncio
async def test_solve_adds_one_charging_stop(monkeypatch):
    vehicle = {
        "id": "car-1",
        "ac_charger": {"ports": ["type2", "schuko"]},
        "dc_charger": {"ports": ["ccs"]},
        "energy_consumption": {"average_consumption": 20},
    }

    station = {
        "id": 1,
        "lat_lon": (0.0, 1.0),  # format lat, lon
        "connectors": [
            {"plug_id": 33}
        ],
    }

    route_calls = {"count": 0}

    def fake_calculate_route(points, steps=False):
        route_calls["count"] += 1

        # Pierwsza trasa: start -> end, za długa na zasięg
        if points == [(0, 0), (3, 0)]:
            return (
                300,
                180,
                [(0, 0), (1, 0), (2, 0), (3, 0)],
                []
            )

        # Dojazd do stacji
        if points == [(0, 0), (1.0, 0.0)]:
            return (
                100,
                60,
                [(0, 0), (1.0, 0.0)],
                []
            )

        # Stacja -> koniec
        if points == [(1.0, 0.0), (3, 0)]:
            return (
                100,
                70,
                [(1.0, 0.0), (3, 0)],
                []
            )

        # Pełna trasa start -> stacja -> koniec
        if points == [(0, 0), (1.0, 0.0), (3, 0)]:
            return (
                200,
                130,
                [(0, 0), (1.0, 0.0), (3, 0)],
                []
            )

        raise AssertionError(f"Unexpected route points: {points}")

    monkeypatch.setattr(
        ra,
        "get_car_range_and_battery_capacity",
        lambda car_id: (200, 100, vehicle)
    )

    monkeypatch.setattr(
        ra,
        "get_temperature_async",
        lambda lat, lon, date: async_return({"temp": 20})
    )

    monkeypatch.setattr(
        ra,
        "get_charging_stations_async_max_result_",
        lambda lat, lon, max_result, distance: async_return([station])
    )

    monkeypatch.setattr(
        ra,
        "calculate_route",
        fake_calculate_route
    )

    monkeypatch.setattr(
        ra,
        "calculate_charging_time",
        lambda battery_capacity, plug_id, start_value, goal_value: 30
    )

    monkeypatch.setattr(
        ra,
        "calculate_electricity_cost",
        lambda waypoints, avg_consumption, dist: async_return(50.0)
    )

    result = await ra.solve(
        start_point=(0, 0),
        end_point=(3, 0),
        carId="car-1",
        dateTime=datetime(2026, 1, 1, 12, 0)
    )

    chargings, dist, time, coordinates, total_time, cost = result

    assert chargings["cords"] == [(1.0, 0.0)]
    assert chargings["times"] == [30]
    assert chargings["charger_info"][0]["id"] == 1
    assert chargings["plugs"][0]["key"] == "ccs"

    assert dist == 200
    assert time == 130
    assert total_time == 160
    assert cost == 50.0


@pytest.mark.asyncio
async def test_solve_raises_when_no_charger_found(monkeypatch):
    vehicle = {
        "id": "car-1",
        "ac_charger": {"ports": ["type2"]},
        "dc_charger": {"ports": ["ccs"]},
        "energy_consumption": {"average_consumption": 20},
    }

    monkeypatch.setattr(
        ra,
        "get_car_range_and_battery_capacity",
        lambda car_id: (200, 100, vehicle)
    )

    monkeypatch.setattr(
        ra,
        "get_temperature_async",
        lambda lat, lon, date: async_return({"temp": 20})
    )

    monkeypatch.setattr(
        ra,
        "calculate_route",
        lambda points, steps=False: (
            300,
            180,
            [(0, 0), (1, 0), (2, 0), (3, 0)],
            []
        )
    )

    monkeypatch.setattr(
        ra,
        "get_charging_stations_async_max_result_",
        lambda lat, lon, max_result, distance: async_return([])
    )

    with pytest.raises(Exception, match="Could not find a charger"):
        await ra.solve(
            start_point=(0, 0),
            end_point=(3, 0),
            carId="car-1",
            dateTime=datetime(2026, 1, 1, 12, 0)
        )


@pytest.mark.asyncio
async def test_solve_uses_charging_to_100(monkeypatch):
    vehicle = {
        "id": "car-1",
        "ac_charger": {"ports": ["type2"]},
        "dc_charger": {"ports": ["ccs"]},
        "energy_consumption": {"average_consumption": 20},
    }

    seen = {
        "goal_value": None
    }

    station = {
        "id": 1,
        "lat_lon": (0.0, 1.0),
        "connectors": [
            {"plug_id": 33}
        ],
    }

    def fake_calculate_route(points, steps=False):
        if points == [(0, 0), (3, 0)]:
            return 300, 180, [(0, 0), (1, 0), (2, 0), (3, 0)], []
        if points == [(0, 0), (1.0, 0.0)]:
            return 100, 60, [(0, 0), (1.0, 0.0)], []
        if points == [(1.0, 0.0), (3, 0)]:
            return 100, 70, [(1.0, 0.0), (3, 0)], []
        if points == [(0, 0), (1.0, 0.0), (3, 0)]:
            return 200, 130, [(0, 0), (1.0, 0.0), (3, 0)], []
        raise AssertionError(f"Unexpected route points: {points}")

    def fake_calculate_charging_time(battery_capacity, plug_id, start_value, goal_value):
        seen["goal_value"] = goal_value
        return 40

    monkeypatch.setattr(
        ra,
        "get_car_range_and_battery_capacity",
        lambda car_id: (200, 100, vehicle)
    )

    monkeypatch.setattr(
        ra,
        "get_temperature_async",
        lambda lat, lon, date: async_return({"temp": 20})
    )

    monkeypatch.setattr(
        ra,
        "get_charging_stations_async_max_result_",
        lambda lat, lon, max_result, distance: async_return([station])
    )

    monkeypatch.setattr(ra, "calculate_route", fake_calculate_route)
    monkeypatch.setattr(ra, "calculate_charging_time", fake_calculate_charging_time)

    monkeypatch.setattr(
        ra,
        "calculate_electricity_cost",
        lambda waypoints, avg_consumption, dist: async_return(50.0)
    )

    await ra.solve(
        start_point=(0, 0),
        end_point=(3, 0),
        carId="car-1",
        dateTime=datetime(2026, 1, 1, 12, 0),
        charging_to_100=True
    )

    assert seen["goal_value"] == 1.0


def async_return(value):
    async def inner(*args, **kwargs):
        return value

    return inner()