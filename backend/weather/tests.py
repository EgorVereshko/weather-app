from unittest.mock import Mock, patch

from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from weather.services import FORECAST_URL, GEOCODING_URL


def open_meteo_response(data):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = data
    return response


def sample_forecast():
    return {
        "timezone": "Europe/Amsterdam",
        "current": {
            "time": "2026-11-10T12:00",
            "temperature_2m": 12.5,
            "apparent_temperature": 11.2,
            "relative_humidity_2m": 68,
            "wind_speed_10m": 13.4,
            "weather_code": 2,
        },
        "daily": {
            "time": [f"2026-11-{day:02d}" for day in range(10, 17)],
            "temperature_2m_max": [13.0] * 7,
            "temperature_2m_min": [7.0] * 7,
            "weather_code": [2] * 7,
        },
    }


class WeatherApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_existing_city_returns_current_weather_and_seven_days(self):
        location = {
            "name": "Amsterdam",
            "country": "Netherlands",
            "country_code": "NL",
            "admin1": "North Holland",
            "latitude": 52.37,
            "longitude": 4.89,
            "population": 921402,
        }
        with patch(
            "weather.services.requests.get",
            side_effect=[
                open_meteo_response({"results": [location]}),
                open_meteo_response(sample_forecast()),
            ],
        ) as get:
            response = self.client.get("/api/weather/", {"city": "Amsterdam"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["city"]["name"], "Amsterdam")
        self.assertEqual(response.data["city"]["country"], "Netherlands")
        self.assertEqual(response.data["current"]["condition"]["description"], "Переменная облачность")
        self.assertEqual(len(response.data["forecast"]), 7)
        self.assertEqual(get.call_count, 2)
        self.assertEqual(get.call_args_list[0].args[0], GEOCODING_URL)
        self.assertEqual(get.call_args_list[1].args[0], FORECAST_URL)
        self.assertEqual(get.call_args_list[1].kwargs["params"]["forecast_days"], 7)
        self.assertEqual(get.call_args_list[0].kwargs["timeout"], 8)
        self.assertEqual(
            get.call_args_list[0].kwargs["proxies"],
            {"http": None, "https": None},
        )

    def test_unknown_city_returns_404(self):
        with patch(
            "weather.services.requests.get",
            return_value=open_meteo_response({"generationtime_ms": 0.35}),
        ):
            response = self.client.get("/api/weather/", {"city": "NotARealCity"})

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["code"], "city_not_found")
        self.assertNotIn("traceback", str(response.data).lower())

    def test_missing_and_blank_city_return_400_without_upstream_request(self):
        with patch("weather.services.requests.get") as get:
            missing = self.client.get("/api/weather/")
            blank = self.client.get("/api/weather/", {"city": "  "})

        self.assertEqual(missing.status_code, 400)
        self.assertEqual(blank.status_code, 400)
        self.assertEqual(missing.data["code"], "missing_city")
        get.assert_not_called()

    def test_upstream_request_error_returns_502(self):
        import requests

        with patch(
            "weather.services.requests.get",
            side_effect=requests.Timeout("upstream timeout"),
        ):
            response = self.client.get("/api/weather/", {"city": "Amsterdam"})

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.data["code"], "upstream_error")
        self.assertNotIn("timeout", response.data["message"].lower())

    def test_malformed_geocoding_response_returns_502(self):
        with patch(
            "weather.services.requests.get",
            return_value=open_meteo_response({"results": "invalid"}),
        ):
            response = self.client.get("/api/weather/", {"city": "Amsterdam"})

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.data["code"], "invalid_upstream_response")

    def test_geocoding_response_without_results_or_metadata_returns_502(self):
        with patch(
            "weather.services.requests.get",
            return_value=open_meteo_response({}),
        ):
            response = self.client.get("/api/weather/", {"city": "Amsterdam"})

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.data["code"], "invalid_upstream_response")

    def test_malformed_forecast_data_returns_502(self):
        location = {
            "name": "Amsterdam",
            "country": "Netherlands",
            "latitude": 52.37,
            "longitude": 4.89,
        }
        malformed_forecast = sample_forecast()
        malformed_forecast["daily"]["temperature_2m_max"] = [12.0]
        with patch(
            "weather.services.requests.get",
            side_effect=[
                open_meteo_response({"results": [location]}),
                open_meteo_response(malformed_forecast),
            ],
        ):
            response = self.client.get("/api/weather/", {"city": "Amsterdam"})

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.data["code"], "invalid_upstream_response")

    def test_successful_city_response_is_cached(self):
        location = {
            "name": "Amsterdam",
            "country": "Netherlands",
            "latitude": 52.37,
            "longitude": 4.89,
        }
        with patch(
            "weather.services.requests.get",
            side_effect=[
                open_meteo_response({"results": [location]}),
                open_meteo_response(sample_forecast()),
            ],
        ) as get:
            first = self.client.get("/api/weather/", {"city": "Amsterdam"})
            second = self.client.get("/api/weather/", {"city": "AMSTERDAM"})

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data, second.data)
        self.assertEqual(get.call_count, 2)
