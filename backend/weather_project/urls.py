from django.urls import path

from weather.views import weather_by_city


urlpatterns = [
    path("api/weather/", weather_by_city, name="weather-by-city"),
]
