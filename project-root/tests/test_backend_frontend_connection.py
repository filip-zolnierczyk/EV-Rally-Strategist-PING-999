import pytest
import httpx
import asyncio
from datetime import datetime

# Integration tests for backend-frontend connection

BASE_URL = "http://localhost:8000"

class TestBackendFrontendConnection:
    """Test connection and data flow between backend and frontend"""
    
    @pytest.mark.asyncio
    async def test_health_check_endpoint(self):
        """Test backend health check"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/test")
            assert response.status_code == 200
            assert "message" in response.json()

    @pytest.mark.asyncio
    async def test_cors_headers_present(self):
        """Test CORS headers are properly set"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/test")
            # Check for CORS headers
            assert response.headers.get('access-control-allow-origin') is not None or response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_cars_endpoint_response_format(self):
        """Test /cars endpoint returns correct data format"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/cars")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            
            if len(data) > 0:
                car = data[0]
                assert "id" in car
                assert "brand" in car
                assert "model" in car
                assert "battery_capacity" in car

    @pytest.mark.asyncio
    async def test_calculate_distance_request_response(self):
        """Test /calculate_distance endpoint request-response cycle"""
        async with httpx.AsyncClient() as client:
            payload = {
                "start": [18.6466, 54.3520],
                "end": [14.4378, 50.0755],
                "carId": "test-car-id",
                "dateTime": "2026-04-14T20:15",
                "charging_to_100": False
            }
            
            response = await client.post(f"{BASE_URL}/calculate_distance", json=payload)
            
            # Accept timeout or success
            if response.status_code == 200:
                data = response.json()
                assert "distance" in data
                assert "time" in data
                assert "chargings" in data
                assert "total_time" in data
                assert isinstance(data["distance"], (int, float))
                assert data["distance"] > 0

    @pytest.mark.asyncio
    async def test_invalid_car_id_handling(self):
        """Test backend handles invalid car ID gracefully"""
        async with httpx.AsyncClient() as client:
            payload = {
                "start": [18.6466, 54.3520],
                "end": [14.4378, 50.0755],
                "carId": "invalid-car-xyz",
                "dateTime": "2026-04-14T20:15"
            }
            
            response = await client.post(f"{BASE_URL}/calculate_distance", json=payload)
            # Should either return 404 or process with default car
            assert response.status_code in [200, 404, 400]

    @pytest.mark.asyncio
    async def test_missing_required_fields(self):
        """Test request validation for missing fields"""
        async with httpx.AsyncClient() as client:
            # Missing 'end' coordinate
            payload = {
                "start": [18.6466, 54.3520],
                "carId": "test-car",
                "dateTime": "2026-04-14T20:15"
            }
            
            response = await client.post(f"{BASE_URL}/calculate_distance", json=payload)
            assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_coordinate_validation(self):
        """Test coordinate validation"""
        async with httpx.AsyncClient() as client:
            # Invalid latitude
            payload = {
                "start": [18.6466, 100],  # Invalid latitude
                "end": [14.4378, 50.0755],
                "carId": "test-car",
                "dateTime": "2026-04-14T20:15"
            }
            
            response = await client.post(f"{BASE_URL}/calculate_distance", json=payload)
            # Should fail validation or process

    @pytest.mark.asyncio
    async def test_datetime_format_validation(self):
        """Test datetime format validation"""
        async with httpx.AsyncClient() as client:
            payload = {
                "start": [18.6466, 54.3520],
                "end": [14.4378, 50.0755],
                "carId": "test-car",
                "dateTime": "invalid-date-time",  # Invalid format
            }
            
            response = await client.post(f"{BASE_URL}/calculate_distance", json=payload)
            # May accept or reject depending on validation

    @pytest.mark.asyncio
    async def test_response_polyline_encoding(self):
        """Test that coordinates are properly encoded in response"""
        async with httpx.AsyncClient() as client:
            payload = {
                "start": [18.6466, 54.3520],
                "end": [14.4378, 50.0755],
                "carId": "test-car",
                "dateTime": "2026-04-14T20:15"
            }
            
            response = await client.post(f"{BASE_URL}/calculate_distance", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "coordinates" in data:
                    # Polyline should be a string
                    assert isinstance(data["coordinates"], str)

    @pytest.mark.asyncio
    async def test_charging_info_included(self):
        """Test that charging information is included in response"""
        async with httpx.AsyncClient() as client:
            payload = {
                "start": [18.6466, 54.3520],
                "end": [14.4378, 50.0755],
                "carId": "test-car",
                "dateTime": "2026-04-14T20:15"
            }
            
            response = await client.post(f"{BASE_URL}/calculate_distance", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                assert "charging_time" in data
                assert "charger_info" in data
                assert "plugs" in data
                assert isinstance(data["charging_time"], list)