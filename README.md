# Kelishim — реестр обещаний аренды

Мобильный-first прототип: источники → извлечение условий → сравнение → вопросы хозяину → ответ → итог сделки.

## Запуск

Backend (Python 3.10+, FastAPI):

```bash
pip install -r backend/requirements.txt
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
- `backend/adapters/muse_adapter.py` — тонкие адаптеры `transcribe/ocr/extract/draft_questions/draft_owner_message/translate_kg`, timeout 30с, 1 retry, сбой → `ManualInputRequired` (ручной ввод, не белый экран).
- `backend/store.py + app.py` — FastAPI + JSON-файл на сделку, пересчёт реестра кодом после каждого источника.
- `frontend/src/` — React: старт/demo, реестр (иконка+слово, цитаты), вопросы только по `conflict/unknown` + ручное подтверждение, ответ хозяина, итог. Юр.оговорка закреплена внизу всегда.

## Ограничения (неподвижные)

Не определяем мошенничество/риск/собственность/юр. силу; не скрейпим объявления; ничего не отправляем автоматически; решение match/conflict — код; схема 10 полей меняется только решением владельца.

## Demo: real vs saved

Backend без реального ключа Muse работает на ручном вводе и demo-примере (значения вводит пользователь/пример, статусы считает код). Сохранённый результат допускается только с явной меткой «сохранённый результат». Реальный API не подтверждён — см. `docs/muse-contract.md`.

## Команды тестов

```bash
python -m pytest backend/tests -q        # 26 passed, 1 skipped (SKIP = реальный Muse API без доки)
PYTHONPATH=. python evals/run.py         # 3/3 eval-образца
cd frontend && npm run build             # tsc + vite build
```

## Статус (Task 0–5)

Task 0 spec → 1 домен → 2 adapter → 3 API → 4 UI → 5 QA. Все тесты зелёные, детали в `docs/superpowers/plans/2026-10-29-kelishim-slices.md`.
