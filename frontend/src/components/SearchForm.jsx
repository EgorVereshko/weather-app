import { useState } from "react";

export default function SearchForm({ onSearch, isLoading }) {
  const [city, setCity] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    onSearch(city);
  }

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <label className="search-form__label" htmlFor="city-search">
        Город
      </label>
      <div className="search-form__controls">
        <span className="search-form__icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none">
            <circle cx="10.8" cy="10.8" r="6.8" />
            <path d="m16 16 4.2 4.2" />
          </svg>
        </span>
        <input
          id="city-search"
          name="city"
          type="search"
          autoComplete="off"
          placeholder="Например, Москва"
          value={city}
          onChange={(event) => setCity(event.target.value)}
          aria-label="Введите название города"
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Ищем…" : "Узнать погоду"}
        </button>
      </div>
      <p className="search-form__hint">
        Введите название на русском или английском
      </p>
    </form>
  );
}
