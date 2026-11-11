# Погода рядом

Fullstack-приложение для поиска текущей погоды и прогноза на семь дней по названию города. React обращается только к Django API; Django получает координаты и погодные данные от Open-Meteo.

## Технологии и источники данных

- Frontend: React, JavaScript, Vite, SCSS.
- Backend: Python, Django, Django REST Framework.
- CORS: `django-cors-headers`.
- Данные: [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api) и [Open-Meteo Forecast API](https://open-meteo.com/en/docs).

Для одноимённых городов Geocoding API возвращает несколько результатов; backend выбирает наиболее населённый и добавляет регион и страну, чтобы показать контекст.

## Структура

```text
backend/
  manage.py
  requirements.txt
  weather/
  weather_project/
frontend/
  src/
    components/
    services/weatherApi.js
    styles/main.scss
  package.json
  vite.config.js
```

Проект не хранит данные в базе. Кэш Django LocMemCache хранит успешные ответы десять минут.

### Django API

В PowerShell из папки проекта:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py runserver
```

API будет доступен на `http://127.0.0.1:8000`.

### React frontend

В отдельном терминале из папки проекта:

```powershell
cd frontend
npm install
npm run dev
```

Frontend будет доступен на `http://127.0.0.1:5173`.

## Проверки

Из `backend`:

```powershell
python manage.py test
```

Из `frontend`:

```powershell
npm test
npm run build
```

Backend-тесты проверяют успешный поиск и недельный прогноз, неизвестный город, пустой параметр, ошибку и некорректный ответ Open-Meteo, а также кэширование. Frontend-тесты встроенным Node.js test runner проверяют сервисный ответ, ошибки запроса и некорректные данные без дополнительных тестовых библиотек.