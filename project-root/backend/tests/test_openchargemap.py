import unittest

from app.services.openchargemap import transform_charger_data


class TransformChargerDataTests(unittest.TestCase):
    def test_operational_station(self):
        raw = {
            "StatusType": {"Title": "Operational"},
            "AddressInfo": {
                "Title": "Station A",
                "Latitude": 52.1,
                "Longitude": 21.0,
                "AddressLine1": "Main St 1",
            },
            "Connections": [
                {
                    "ConnectionType": {"Title": "Type 2"},
                    "ConnectionTypeID": 25,
                    "PowerKW": 50,
                    "Amps": 200,
                    "Voltage": 400,
                }
            ],
        }

        result = transform_charger_data(raw)

        self.assertEqual(result["name"], "Station A")
        self.assertEqual(result["lat_lon"], [52.1, 21.0])
        self.assertEqual(result["address"], "Main St 1")
        self.assertEqual(result["connectors"][0]["plug"], "Type 2")
        self.assertEqual(result["connectors"][0]["plug_id"], 25)

    def test_non_operational_station(self):
        raw = {"StatusType": {"Title": "Temporarily Closed"}}

        self.assertEqual(transform_charger_data(raw), {})

    def test_missing_status(self):
        raw = {"StatusType": None}

        self.assertEqual(transform_charger_data(raw), {})


if __name__ == "__main__":
    unittest.main()
