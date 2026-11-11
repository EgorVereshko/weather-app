export default function WeatherIcon({ condition, size = "large" }) {
  return (
    <span
      className={`weather-icon weather-icon--${size}`}
      role="img"
      aria-label={condition.description}
    >
      {condition.icon}
    </span>
  );
}
