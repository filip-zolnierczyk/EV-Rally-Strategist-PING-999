import unittest
from unittest.mock import patch

from app.services import osrm


class OsrmServiceTests(unittest.TestCase):
    def test_convert_to_lonlat(self):
        self.assertEqual(osrm.convert_to_lonlat((52.1, 21.0)), (21.0, 52.1))

    def test_coordinates_to_str(self):
        self.assertEqual(osrm.coordinates_to_str((21.0, 52.1)), "21.0,52.1")

    def test_coordinates_to_tuple_with_spaces(self):
        self.assertEqual(osrm.coordinates_to_tuple(" 52.1 , 21.0 "), (21.0, 52.1))

    @patch("app.services.osrm.requests.get")
    def test_calculate_distance_uses_response(self, mock_get):
        mock_get.return_value.json.return_value = {
            "routes": [{"distance": 12500, "duration": 900}]
        }

        distance_km, duration_min = osrm.calculate_distance((21.0, 52.1), (22.0, 53.1))

        self.assertEqual(distance_km, 12.5)
        self.assertEqual(duration_min, 15)

    @patch("app.services.osrm.requests.get")
    def test_calculate_route_uses_response(self, mock_get):
        mock_get.return_value.json.return_value = {
            "routes": [
                {
                    "distance": 20000,
                    "duration": 1800,
                    "geometry": {"coordinates": [[21.0, 52.1], [22.0, 53.1]]},
                }
            ]
        }

        distance_km, duration_min, coordinates = osrm.calculate_route(
            [(21.0, 52.1), (22.0, 53.1)]
        )

        self.assertEqual(distance_km, 20)
        self.assertEqual(duration_min, 30)
        self.assertEqual(coordinates, [[21.0, 52.1], [22.0, 53.1]])


if __name__ == "__main__":
    unittest.main()
