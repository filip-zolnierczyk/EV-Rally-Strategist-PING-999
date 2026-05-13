import pytest

from app.services.ev_logic import (
    can_vehicle_charge_with_connector,
    calculate_range,
    calculate_charging_time,
    calculate_charging_time_ac,
    calculate_charging_time_dc,
)


def test_vehicle_can_charge_with_ac_type2():
    vehicle = {
        "ac_charger": {
            "ports": ["type2"]
        }
    }

    connector = {
        "plug_id": 25
    }

    result = can_vehicle_charge_with_connector(vehicle, connector)

    assert result == (True, 25, 11.0)


def test_vehicle_can_charge_with_dc_ccs():
    vehicle = {
        "dc_charger": {
            "ports": ["ccs"]
        }
    }

    connector = {
        "plug_id": 33
    }

    result = can_vehicle_charge_with_connector(vehicle, connector)

    assert result == (True, 33, 150.0)


def test_vehicle_cannot_charge_with_wrong_dc_connector():
    vehicle = {
        "dc_charger": {
            "ports": ["ccs"]
        }
    }

    connector = {
        "plug_id": 2  # CHAdeMO
    }

    result = can_vehicle_charge_with_connector(vehicle, connector)

    assert result == (False, 2, 0)


def test_unknown_plug_id_returns_false():
    vehicle = {}

    connector = {
        "plug_id": 999999
    }

    result = can_vehicle_charge_with_connector(vehicle, connector)

    assert result == (False, "Nieznany typ wtyczki", 0)


def test_schuko_is_compatible_when_ac_exists():
    vehicle = {
        "ac_charger": {
            "ports": []
        }
    }

    connector = {
        "plug_id": 28
    }

    result = can_vehicle_charge_with_connector(vehicle, connector)

    assert result == (True, 28, 2.3)


def test_calculate_range_none_temperature():
    result = calculate_range(400, None)

    assert result == 400


def test_calculate_range_optimal_temperature():
    result = calculate_range(400, {"temp": 20})

    assert result == 400


def test_calculate_range_lower_temperature():
    result = calculate_range(400, {"temp": 10})

    assert result == pytest.approx(320)
    # delta = 10
    # factor = 1 - 0.02 * 10 = 0.8
    # 400 * 0.8 = 320


def test_calculate_range_clamped_minimum():
    result = calculate_range(400, {"temp": -50})

    assert result == pytest.approx(240)
    # minimum factor = 0.6
    # 400 * 0.6 = 240


def test_calculate_charging_time_ac_to_80_percent():
    result = calculate_charging_time_ac(
        battery_capacity=100,
        charger_param=10,
        start_value=0.2,
        goal_value=0.8
    )

    assert result == pytest.approx(360)
    # 100 kWh * 0.6 = 60 kWh
    # 60 / 10 * 60 = 360 min


def test_calculate_charging_time_ac_above_80_percent_slower():
    result = calculate_charging_time_ac(
        battery_capacity=100,
        charger_param=10,
        start_value=0.8,
        goal_value=1.0
    )

    assert result == pytest.approx(240)
    # 20 kWh ładowane mocą 5 kW
    # 20 / 5 * 60 = 240 min


def test_calculate_charging_time_ac_when_already_charged():
    result = calculate_charging_time_ac(
        battery_capacity=100,
        charger_param=10,
        start_value=0.8,
        goal_value=0.8
    )

    assert result == 0.0


def test_calculate_charging_time_dc_basic():
    result = calculate_charging_time_dc(
        battery_capacity=100,
        charger_power_kw=100,
        start_value=0.0,
        goal_value=0.2,
        vehicle_max_dc_kw=100
    )

    assert result == pytest.approx(13.333333, rel=1e-3)
    # 20 kWh / 90 kW * 60 = 13.33 min


def test_calculate_charging_time_dc_uses_lower_available_power():
    result = calculate_charging_time_dc(
        battery_capacity=100,
        charger_power_kw=200,
        start_value=0.0,
        goal_value=0.2,
        vehicle_max_dc_kw=100
    )

    assert result == pytest.approx(13.333333, rel=1e-3)


def test_calculate_charging_time_dc_invalid_battery():
    with pytest.raises(ValueError):
        calculate_charging_time_dc(
            battery_capacity=0,
            charger_power_kw=100
        )


def test_calculate_charging_time_unknown_plug_id():
    with pytest.raises(Exception):
        calculate_charging_time(
            battery_capacity=100,
            plug_id=999999
        )


def test_calculate_charging_time_dispatches_to_ac():
    result = calculate_charging_time(
        battery_capacity=100,
        plug_id=25,
        start_value=0.15,
        goal_value=0.8
    )

    assert result == pytest.approx(354.5454545)
    # Type2 ma 11 kW
    # 65 kWh / 11 * 60 = 354.54 min


def test_calculate_charging_time_dispatches_to_dc():
    result = calculate_charging_time(
        battery_capacity=100,
        plug_id=33,
        start_value=0.0,
        goal_value=0.2
    )

    assert result == pytest.approx(8.888888, rel=1e-3)
    # CCS ma 150 kW
    # 20 kWh / (150 * 0.9) * 60 = 8.88 min