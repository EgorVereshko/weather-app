import ForecastCard from "./ForecastCard.jsx";

export default function Forecast({ days }) {
  return (
    <section className="forecast-section" aria-labelledby="forecast-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">ЧТО БУДЕТ ДАЛЬШЕ</p>
          <h2 id="forecast-title">Прогноз на неделю</h2>
        </div>
        <span className="section-heading__unit">День · мин / макс</span>
      </div>
      <div className="forecast-grid">
        {days.map((day) => (
          <ForecastCard key={day.date} day={day} />
        ))}
      </div>
    </section>
  );
}
