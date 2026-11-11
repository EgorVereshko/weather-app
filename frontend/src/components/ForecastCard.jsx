import WeatherIcon from "./WeatherIcon.jsx";

export default function ForecastCard({ day }) {
  const date = new Date(`${day.date}T12:00:00`);
  const weekday = new Intl.DateTimeFormat("ru-RU", {
    weekday: "short",
  }).format(date);
  const dayOfMonth = new Intl.DateTimeFormat("ru-RU", {
    day: "numeric",
    month: "short",
  }).format(date);

  return (
    <article className="forecast-card">
      <div className="forecast-card__date">
        <strong>{weekday}</strong>
        <span>{dayOfMonth}</span>
      </div>
      <WeatherIcon condition={day.condition} size="small" />
      <p className="forecast-card__condition">{day.condition.description}</p>
      <div className="forecast-card__temperatures">
        <strong>{Math.round(day.temperature_max_c)}°</strong>
        <span>{Math.round(day.temperature_min_c)}°</span>
      </div>
    </article>
  );
}
