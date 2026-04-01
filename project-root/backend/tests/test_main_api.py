import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


class MainApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_test_endpoint_returns_backend_message(self):
        response = self.client.get("/test")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Backend działa"})

    @patch("app.main.polyline.encode", return_value="encoded-polyline")
    @patch("app.main.solve")
    def test_calculate_distance_returns_expected_payload(self, mock_solve, mock_encode):
        mock_solve.return_value = (
            [(21.0, 52.1)],
            123.4,
            150.0,
            [(21.0, 52.1), (22.0, 53.1)],
        )

        response = self.client.post(
            "/calculate_distance",
            json={"start": [52.1, 21.0], "end": [53.1, 22.0]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "chargings": [[21.0, 52.1]],
                "distance": 123.4,
                "time": 150.0,
                "coordinates": "encoded-polyline",
            },
        )

        mock_solve.assert_called_once_with((52.1, 21.0), (53.1, 22.0))
        mock_encode.assert_called_once_with([(52.1, 21.0), (53.1, 22.0)])


if __name__ == "__main__":
    unittest.main()
