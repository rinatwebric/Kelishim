# Meta Model API — подтверждённый контракт (проверено 2026-10-29, интернет)

- Обзор/base/auth: https://dev.meta.ai/docs/overview
  `https://api.meta.ai/v1`, Bearer `MODEL_API_KEY` (ключи `LLM_...`),
  модели `muse-spark-1.3` (дефолт), `muse-spark-1.2/1.1`, `muse-wonder-1.0`.
- Structured output: https://dev.meta.ai/docs/structured-output
  Chat Completions `response_format: {type: json_schema, json_schema: {...}}`,
  декодинг ограничен схемой; ответ — JSON-строка в `choices[0].message.content`.
- Auth: https://dev.meta.ai/docs/authentication — ключ только сервером
  (env `MODEL_API_KEY`), никогда во frontend, не в git.
- ASR: https://dev.meta.ai/docs/speech-to-text
  `POST https://api.meta.ai/v1/asr/transcribe`, multipart `request` JSON +
  `audio` WAV mono 16-bit 16/24 kHz, модель `muse-voice-transcribe-1.0`;
  лимиты 32 MB / 10 мин; 429 → backoff; 500 → 1 retry.
  Realtime `wss://api.meta.ai/v1/asr/realtime` для прототипа не используем.
- OCR: image understanding через chat completions `image_url` (data URL) +
  structured output из изображений (там же, structured-output).

## Как подключено

- `backend/adapters/meta_transport.py` — `MetaClient` (httpx):
  `complete()` → `/chat/completions` с `json_schema` на 10 термов (enum),
  `transcribe()` → `/asr/transcribe` multipart,
  `ocr()` → `/chat/completions` с `image_url`.
- `POST /extract` — прогоняет `raw_text` через `MuseAdapter.extract`
  (валидация quote/confidence + retry×1 + timeout 30с сохранены).
  Без `MODEL_API_KEY`: **503 + текст про ручной ввод**, никакого фейка.
- Живой тест: `test_real_api_live_only_with_key` — запускается только
  при наличии `MODEL_API_KEY` в env, иначе SKIP.

## Запуск с ключом

```bash
export MODEL_API_KEY="LLM_..."
uvicorn backend.app:app --port 8000
curl -X POST localhost:8000/extract -H 'Content-Type: application/json' \
  -d '{"raw_text":"аренда 30000 сом, залог 30000"}'
```
