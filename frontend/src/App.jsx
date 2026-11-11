import { useEffect, useRef, useState } from "react";
import CurrentWeather from "./components/CurrentWeather.jsx";
import Forecast from "./components/Forecast.jsx";
import Loading from "./components/Loading.jsx";
import MessageCard from "./components/MessageCard.jsx";
import SearchForm from "./components/SearchForm.jsx";
import { fetchWeather, WeatherApiError } from "./services/weatherApi.js";

export default function App() {
  const [status, setStatus] = useState("initial");
  const [weather, setWeather] = useState(null);
  const [searchedCity, setSearchedCity] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const requestController = useRef(null);

  useEffect(
    () => () => {
      requestController.current?.abort();
    },
    [],
  );

  async function handleSearch(value) {
    const city = value.trim();
    if (!city) {
      requestController.current?.abort();
      requestController.current = null;
      setWeather(null);
      setSearchedCity("");
      setErrorMessage("");
      setStatus("empty");
      return;
    }

    requestController.current?.abort();
    const controller = new AbortController();
    requestController.current = controller;
    setWeather(null);
    setSearchedCity(city);
    setErrorMessage("");
    setStatus("loading");

    try {
      const result = await fetchWeather(city, { signal: controller.signal });
      if (requestController.current === controller) {
        setWeather(result);
        setStatus("success");
      }
    } catch (error) {
      if (error.name === "AbortError") {
        return;
      }
      if (requestController.current !== controller) {
        return;
      }
      if (error instanceof WeatherApiError && error.status === 404) {
        setStatus("notFound");
      } else {
        setErrorMessage(
          error instanceof WeatherApiError
            ? error.message
            : "Не удалось загрузить погоду. Попробуйте ещё раз.",
        );
        setStatus("error");
      }
    }
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <a className="brand" href="/" aria-label="Погода рядом — на главную">
          <span className="brand__mark" aria-hidden="true">
            <svg viewBox="0 0 36 36" fill="none">
              <circle cx="15" cy="15" r="7" />
              <path d="M15 2v3M15 25v3M2 15h3m20 0h3M5.8 5.8 8 8m14 14 2.2 2.2m0-18.4L22 8M8 22l-2.2 2.2" />
              <path d="M21 25.5a5 5 0 0 1 9.8 1.3 3.3 3.3 0 0 1-.7 6.5H20.7a3.3 3.3 0 0 1 .3-6.6" />
            </svg>
          </span>
          <span>погода<span className="brand__accent">рядом</span></span>
        </a>
        <span className="data-source">ДАННЫЕ OPEN-METEO</span>
      </header>

      <section className="hero">
        <div className="hero__copy">
          <p className="eyebrow">ВАША ПОГОДА — БЕЗ ЛИШНИХ СЛОВ</p>
          <h1>
            За окном
            <br />
            <span>где-то рядом.</span>
          </h1>
          <p className="hero__description">
            Узнайте, что взять с собой, где бы вы ни были.
          </p>
        </div>
        <div className="hero__art" aria-hidden="true">
          <span className="hero__sun" />
          <span className="hero__cloud hero__cloud--back" />
          <span className="hero__cloud hero__cloud--front" />
        </div>
      </section>

      <section className="search-panel" aria-label="Поиск погоды">
        <SearchForm onSearch={handleSearch} isLoading={status === "loading"} />
      </section>

      <div className="results" aria-live="polite">
        {status === "initial" && (
          <MessageCard kind="hint" title="Начните с поиска города">
            Например, введите Amsterdam, Казань или Tokyo.
          </MessageCard>
        )}
        {status === "empty" && (
          <MessageCard kind="empty" title="Введите название города">
            Поле поиска не должно быть пустым.
          </MessageCard>
        )}
        {status === "loading" && <Loading city={searchedCity} />}
        {status === "notFound" && (
          <MessageCard kind="error" title="Такой город не найден">
            Проверьте написание или попробуйте ввести название на английском.
          </MessageCard>
        )}
        {status === "error" && (
          <MessageCard kind="error" title="Не удалось загрузить прогноз">
            {errorMessage}
          </MessageCard>
        )}
        {status === "success" && weather && (
          <div className="weather-results">
            <CurrentWeather weather={weather} />
            <Forecast days={weather.forecast} />
          </div>
        )}
      </div>

      <footer className="app-footer">
        <span>Погода рядом</span>
        <span>Прогноз на основе данных Open-Meteo</span>
      </footer>
    </main>
  );
}
