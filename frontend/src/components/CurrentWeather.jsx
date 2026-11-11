import WeatherIcon from "./WeatherIcon.jsx";

function formatTime(value) {
  if (!value) {
    return "";
  }
  return new Intl.DateTimeFormat("ru-RU", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export default function CurrentWeather({ weather }) {
  const { city, current, timezone } = weather;
  const location = [city.region, city.country].filter(Boolean).join(", ");

  return (
    <section className="current-card" aria-labelledby="current-title">
      <div className="current-card__topline">
        <div>
          <p className="eyebrow">СЕЙЧАС В ГОРОДЕ</p>
          <h2 id="current-title">{city.name}</h2>
          <p className="current-card__location">
            {location}
            {timezone && <span> · {timezone}</span>}
          </p>
        </div>
        <div className="current-card__condition">
          <WeatherIcon condition={current.condition} />
          <span>{current.condition.description}</span>
        </div>
      </div>

      <div className="current-card__temperature">
        <span>{Math.round(current.temperature_c)}°</span>
        <p>Ощущается как {Math.round(current.apparent_temperature_c)}°</p>
      </div>

      <div className="current-card__details">
        <div className="weather-detail">
          <span className="weather-detail__icon" aria-hidden="true">↗</span>
          <div>
            <span className="weather-detail__label">Ветер</span>
            <strong>{Math.round(current.wind_speed_kmh)} км/ч</strong>
          </div>
        </div>
        {current.relative_humidity_percent != null && (
          <div className="weather-detail">
            <span className="weather-detail__icon" aria-hidden="true">◌</span>
            <div>
              <span className="weather-detail__label">Влажность</span>
              <strong>{current.relative_humidity_percent}%</strong>
            </div>
          </div>
        )}
        {current.time && (
          <div className="weather-detail">
            <span className="weather-detail__icon" aria-hidden="true">◷</span>
            <div>
              <span className="weather-detail__label">Обновлено</span>
              <strong>{formatTime(current.time)}</strong>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
