export default function Loading({ city }) {
  return (
    <div className="status-card" role="status" aria-live="polite">
      <span className="loading-spinner" aria-hidden="true" />
      <div>
        <strong>Ищем прогноз для {city}…</strong>
        <p>Получаем свежие данные о погоде</p>
      </div>
    </div>
  );
}
