# Kelishim — реестр обещаний аренды

Мобильный-first прототип: источники → извлечение условий → сравнение → вопросы хозяину → ответ → итог сделки.

## Запуск

Backend (Python 3.10+, FastAPI):

```bash
pip install -r backend/requirements.txt
cp .env.example .env     # вписать MODEL_API_KEY=LLM_... (только backend, не в git)
uvicorn backend.app:app --reload --port 8000
```

Frontend (Node 20+, React+Vite+TS+Tailwind):

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173, API по умолчанию http://localhost:8000
VITE_API_URL=http://<host>:8000 npm run dev   # другой backend
```

Без регистрации: открой frontend → «Попробовать на примере».

## Архитектура

- `backend/domain/` — чистое ядро без LLM: `schema.py` (10 условий + цитата/confidence/hedged), `normalize.py` (суммы/валюты/сроки/pets), `registry.py` (`unknown/single/match/conflict` кодом).
- `backend/adapters/meta_transport.py` — реальный Meta Model API (`muse-spark-1.3` + json_schema, ASR, image_url OCR), контракт в `docs/muse-contract.md`.
- `POST /extract` (текст → условия), `POST /transcribe` (аудио ≤32МБ → текст), `POST /ocr` (фото ≤32МБ → текст). Без `MODEL_API_KEY` — 503 + ручной ввод, никакого фейка.
- `backend/store.py + app.py` — FastAPI + JSON-файл на сделку, пересчёт реестра кодом после каждого источника.
- `frontend/src/` — React: старт/demo, реестр (иконка+слово, цитаты), вопросы только по `conflict/unknown` + ручное подтверждение, ответ хозяина, итог. Юр.оговорка закреплена внизу всегда.

## Ограничения (неподвижные)

Не определяем мошенничество/риск/собственность/юр. силу; не скрейпим объявления; ничего не отправляем автоматически; решение match/conflict — код; схема 10 полей меняется только решением владельца.

## Demo: real vs saved

Backend без ключа работает на ручном вводе и demo-примере (значения вводит пользователь/пример, статусы считает код). Сохранённый результат допускается только с явной меткой «сохранённый результат». С ключом (`MODEL_API_KEY` в `.env`) — живой `/extract` через реальный Muse API; во фронте кнопка «✨ Извлечь условия автоматически», фото/аудио через `/ocr`/`/transcribe`.

## Команды тестов

```bash
python -m pytest backend/tests -q        # ~49 passed (живой тест требует MODEL_API_KEY в .env, иначе SKIP)
PYTHONPATH=. python evals/run.py         # 3/3 eval-образца
cd frontend && npm test && npm run build # vitest + tsc + vite build
```

## Статус (Task 0–5)

Task 0 spec → 1 домен → 2 adapter → 3 API → 4 UI → 5 QA. Все тесты зелёные, детали в `docs/superpowers/plans/2026-10-29-kelishim-slices.md`.
