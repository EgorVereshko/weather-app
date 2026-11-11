const API_URL =
  import.meta.env?.VITE_WEATHER_API_URL || "http://127.0.0.1:8000";

export class WeatherApiError extends Error {
  constructor(message, status = 0, code = "request_error") {
    super(message);
    this.name = "WeatherApiError";
    this.status = status;
    this.code = code;
  }
}

function isValidWeather(data) {
  return (
    data &&
    typeof data === "object" &&
    data.city &&
    typeof data.city.name === "string" &&
    typeof data.city.country === "string" &&
    data.current &&
    Number.isFinite(data.current.temperature_c) &&
    Number.isFinite(data.current.apparent_temperature_c) &&
    Number.isFinite(data.current.wind_speed_kmh) &&
    Number.isInteger(data.current.relative_humidity_percent) &&
    data.current.condition &&
    typeof data.current.condition.description === "string" &&
    typeof data.current.condition.icon === "string" &&
    Array.isArray(data.forecast) &&
    data.forecast.length > 0 &&
    data.forecast.every(
      (day) =>
        day &&
        typeof day.date === "string" &&
        Number.isFinite(day.temperature_max_c) &&
        Number.isFinite(day.temperature_min_c) &&
        day.condition &&
        typeof day.condition.description === "string" &&
        typeof day.condition.icon === "string",
    )
  );
}

export async function fetchWeather(city, { signal } = {}) {
  let response;
  try {
    response = await fetch(
      `${API_URL}/api/weather/?${new URLSearchParams({ city })}`,
      { signal },
    );
  } catch (error) {
    if (error.name === "AbortError") {
      throw error;
    }
    throw new WeatherApiError("Не удалось связаться с сервером погоды.");
  }

  let data;
  try {
    data = await response.json();
  } catch (error) {
    if (error.name === "AbortError") {
      throw error;
    }
    throw new WeatherApiError("Сервер вернул некорректный ответ.", response.status);
  }

  if (!response.ok) {
    const message =
      typeof data?.message === "string"
        ? data.message
        : "Не удалось получить прогноз.";
    throw new WeatherApiError(message, response.status, data?.code);
  }

  if (!isValidWeather(data)) {
    throw new WeatherApiError("Сервер вернул некорректный ответ.", response.status);
  }

  return data;
}
