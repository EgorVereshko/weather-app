import logging
import math
import os
from datetime import date as date_type

import requests


logger = logging.getLogger(__name__)
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT_SECONDS = 8
USE_ENV_PROXY = os.getenv("OPEN_METEO_USE_PROXY", "false").lower() == "true"

WEATHER_CONDITIONS = {
    0: ("Ясно", "☀️"),
    1: ("Преимущественно ясно", "🌤️"),
    2: ("Переменная облачность", "⛅"),
    3: ("Пасмурно", "☁️"),
    45: ("Туман", "🌫️"),
    48: ("Изморозь", "🌫️"),
    51: ("Лёгкая морось", "🌦️"),
    53: ("Морось", "🌦️"),
    55: ("Сильная морось", "🌧️"),
    56: ("Ледяная морось", "🌧️"),
    57: ("Сильная ледяная морось", "🌧️"),
    61: ("Небольшой дождь", "🌦️"),
    63: ("Дождь", "🌧️"),
    65: ("Сильный дождь", "🌧️"),
    66: ("Ледяной дождь", "🌧️"),
    67: ("Сильный ледяной дождь", "🌧️"),
    71: ("Небольшой снег", "🌨️"),
    73: ("Снег", "🌨️"),
    75: ("Сильный снег", "❄️"),
    77: ("Снежная крупа", "🌨️"),
    80: ("Кратковременный дождь", "🌦️"),
    81: ("Ливень", "🌧️"),
    82: ("Сильный ливень", "⛈️"),
    85: ("Снегопад", "🌨️"),
    86: ("Сильный снегопад", "❄️"),
    95: ("Гроза", "⛈️"),
    96: ("Гроза с градом", "⛈️"),
    99: ("Сильная гроза с градом", "⛈️"),
}


class OpenMeteoError(Exception):
    pass


class CityNotFoundError(Exception):
    pass


class InvalidOpenMeteoResponse(Exception):
    pass


def describe_weather(code):
    if type(code) is not int or code not in WEATHER_CONDITIONS:
        raise InvalidOpenMeteoResponse("Unsupported weather code")
    description, icon = WEATHER_CONDITIONS[code]
    return {"description": description, "icon": icon}


def _get_json(url, params):
    try:
        request_options = {}
        if not USE_ENV_PROXY:
            request_options["proxies"] = {"http": None, "https": None}
        response = requests.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
            **request_options,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        logger.warning("Open-Meteo request failed: %s", error)
        raise OpenMeteoError from error


def _require_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InvalidOpenMeteoResponse("Expected a numeric value")
    try:
        number = float(value)
    except (OverflowError, ValueError) as error:
        raise InvalidOpenMeteoResponse("Expected a finite numeric value") from error
    if not math.isfinite(number):
        raise InvalidOpenMeteoResponse("Expected a finite numeric value")
    return number


def _require_integer(value):
    number = _require_number(value)
    if not number.is_integer():
        raise InvalidOpenMeteoResponse("Expected an integer value")
    return int(number)


def _condition(code):
    return describe_weather(_require_integer(code))


def _choose_location(results):
    if not isinstance(results, list):
        raise InvalidOpenMeteoResponse("Expected a list of geocoding results")
    if not results:
        raise CityNotFoundError

    valid_results = []
    for result in results:
        if not isinstance(result, dict):
            continue
        try:
            latitude = _require_number(result.get("latitude"))
            longitude = _require_number(result.get("longitude"))
        except InvalidOpenMeteoResponse:
            continue
        if not isinstance(result.get("name"), str) or not result["name"].strip():
            continue
        population = result.get("population", 0)
        if isinstance(population, (int, float)) and not isinstance(population, bool):
            population = max(population, 0)
        else:
            population = 0
        valid_results.append((population, result, latitude, longitude))

    if not valid_results:
        raise InvalidOpenMeteoResponse("No valid geocoding results")

    _, location, latitude, longitude = max(valid_results, key=lambda item: item[0])
    return location, latitude, longitude


def _build_forecast(data, location):
    if not isinstance(data, dict):
        raise InvalidOpenMeteoResponse("Expected a forecast object")

    current = data.get("current")
    daily = data.get("daily")
    if not isinstance(current, dict) or not isinstance(daily, dict):
        raise InvalidOpenMeteoResponse("Forecast is missing current or daily data")
    if not isinstance(data.get("timezone"), str):
        raise InvalidOpenMeteoResponse("Expected a forecast timezone")
    if not isinstance(current.get("time"), str):
        raise InvalidOpenMeteoResponse("Expected a current observation time")

    current_weather = {
        "time": current.get("time"),
        "temperature_c": _require_number(current.get("temperature_2m")),
        "apparent_temperature_c": _require_number(
            current.get("apparent_temperature")
        ),
        "relative_humidity_percent": _require_integer(
            current.get("relative_humidity_2m")
        ),
        "wind_speed_kmh": _require_number(current.get("wind_speed_10m")),
        "condition": _condition(current.get("weather_code")),
    }

    dates = daily.get("time")
    highs = daily.get("temperature_2m_max")
    lows = daily.get("temperature_2m_min")
    codes = daily.get("weather_code")
    if not all(isinstance(values, list) for values in (dates, highs, lows, codes)):
        raise InvalidOpenMeteoResponse("Daily forecast arrays are missing")
    if not 5 <= len(dates) <= 7 or not (
        len(dates) == len(highs) == len(lows) == len(codes)
    ):
        raise InvalidOpenMeteoResponse("Daily forecast arrays have inconsistent lengths")

    forecast = []
    for forecast_date, high, low, code in zip(dates, highs, lows, codes):
        if not isinstance(forecast_date, str):
            raise InvalidOpenMeteoResponse("Expected a forecast date")
        try:
            date_type.fromisoformat(forecast_date)
        except ValueError as error:
            raise InvalidOpenMeteoResponse("Expected a valid forecast date") from error
        forecast.append(
            {
                "date": forecast_date,
                "temperature_max_c": _require_number(high),
                "temperature_min_c": _require_number(low),
                "condition": _condition(code),
            }
        )

    country = location.get("country")
    region = location.get("admin1")
    return {
        "city": {
            "name": location["name"],
            "country": country if isinstance(country, str) else "",
            "country_code": location.get("country_code", ""),
            "region": region if isinstance(region, str) else "",
        },
        "timezone": data["timezone"],
        "units": {"temperature": "°C", "wind_speed": "km/h"},
        "current": current_weather,
        "forecast": forecast,
    }


def get_city_weather(city):
    geocoding = _get_json(
        GEOCODING_URL,
        {"name": city, "count": 10, "language": "ru", "format": "json"},
    )
    if not isinstance(geocoding, dict):
        raise InvalidOpenMeteoResponse("Expected a geocoding object")
    if "results" not in geocoding:
        generation_time = geocoding.get("generationtime_ms")
        if generation_time is not None:
            try:
                _require_number(generation_time)
            except InvalidOpenMeteoResponse as error:
                raise InvalidOpenMeteoResponse(
                    "Invalid geocoding metadata"
                ) from error
            raise CityNotFoundError
        raise InvalidOpenMeteoResponse("Geocoding response is missing results")
    location, latitude, longitude = _choose_location(geocoding["results"])

    forecast = _get_json(
        FORECAST_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,relative_humidity_2m,apparent_temperature,"
                "weather_code,wind_speed_10m"
            ),
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "forecast_days": 7,
            "timezone": "auto",
        },
    )
    return _build_forecast(forecast, location)
