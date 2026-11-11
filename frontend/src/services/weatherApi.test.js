import assert from "node:assert/strict";
import { afterEach, test } from "node:test";
import { fetchWeather, WeatherApiError } from "./weatherApi.js";

const originalFetch = globalThis.fetch;

afterEach(() => {
  globalThis.fetch = originalFetch;
});

function validWeather() {
  return {
    city: { name: "Amsterdam", country: "Netherlands" },
    current: {
      temperature_c: 12,
      apparent_temperature_c: 11,
      wind_speed_kmh: 8,
      relative_humidity_percent: 60,
      condition: { description: "Ясно", icon: "☀️" },
    },
    forecast: [
      {
        date: "2026-11-10",
        temperature_max_c: 14,
        temperature_min_c: 8,
        condition: { description: "Ясно", icon: "☀️" },
      },
    ],
  };
}

test("requests Django and returns a validated forecast", async () => {
  let requestUrl;
  globalThis.fetch = async (url) => {
    requestUrl = url;
    return { ok: true, status: 200, json: async () => validWeather() };
  };

  const weather = await fetchWeather("New York");

  assert.equal(weather.city.name, "Amsterdam");
  assert.match(requestUrl, /\/api\/weather\/\?city=New\+York$/);
});

test("maps a not-found response to WeatherApiError", async () => {
  globalThis.fetch = async () => ({
    ok: false,
    status: 404,
    json: async () => ({ code: "city_not_found", message: "Город не найден." }),
  });

  await assert.rejects(fetchWeather("No such city"), (error) => {
    assert.ok(error instanceof WeatherApiError);
    assert.equal(error.status, 404);
    assert.equal(error.message, "Город не найден.");
    return true;
  });
});

test("rejects malformed JSON and malformed successful responses", async () => {
  globalThis.fetch = async () => ({
    ok: true,
    status: 200,
    json: async () => {
      throw new SyntaxError("invalid JSON");
    },
  });
  await assert.rejects(fetchWeather("Amsterdam"), /некорректный ответ/);

  globalThis.fetch = async () => ({
    ok: true,
    status: 200,
    json: async () => ({ city: {}, forecast: [] }),
  });
  await assert.rejects(fetchWeather("Amsterdam"), /некорректный ответ/);
});

test("converts network failures to a user-facing error", async () => {
  globalThis.fetch = async () => {
    throw new TypeError("network detail");
  };

  await assert.rejects(fetchWeather("Amsterdam"), (error) => {
    assert.ok(error instanceof WeatherApiError);
    assert.equal(error.message, "Не удалось связаться с сервером погоды.");
    assert.doesNotMatch(error.message, /network detail/);
    return true;
  });
});

test("preserves cancellation while reading the response body", async () => {
  globalThis.fetch = async () => ({
    ok: true,
    status: 200,
    json: async () => {
      const error = new Error("cancelled");
      error.name = "AbortError";
      throw error;
    },
  });

  await assert.rejects(fetchWeather("Amsterdam"), (error) => {
    assert.equal(error.name, "AbortError");
    return true;
  });
});
