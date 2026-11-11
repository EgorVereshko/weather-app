import logging

from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response

from weather.services import (
    CityNotFoundError,
    InvalidOpenMeteoResponse,
    OpenMeteoError,
    get_city_weather,
)


logger = logging.getLogger(__name__)


@api_view(["GET"])
def weather_by_city(request):
    city = request.query_params.get("city", "").strip()
    if not city:
        return Response(
            {"code": "missing_city", "message": "Укажите название города."},
            status=400,
        )

    cache_key = f"weather:{city.casefold()}"
    cached_weather = cache.get(cache_key)
    if cached_weather is not None:
        return Response(cached_weather)

    try:
        weather = get_city_weather(city)
    except CityNotFoundError:
        return Response(
            {"code": "city_not_found", "message": "Город не найден."},
            status=404,
        )
    except OpenMeteoError:
        return Response(
            {
                "code": "upstream_error",
                "message": "Сервис погоды временно недоступен. Попробуйте позже.",
            },
            status=502,
        )
    except InvalidOpenMeteoResponse:
        logger.warning("Open-Meteo returned an invalid response")
        return Response(
            {
                "code": "invalid_upstream_response",
                "message": "Сервис погоды вернул некорректные данные.",
            },
            status=502,
        )

    cache.set(cache_key, weather, timeout=600)
    return Response(weather)
