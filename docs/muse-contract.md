# Muse contract (Task 2)

> Реальных endpoint в доке хакатона на 2026-10-29 не подтверждено. Имена ниже — интерфейс адаптера, не внешний API. Выдумывать URL/схему запрещено.

## Интерфейс `MuseAdapter(client, timeout=30)`

- `client.complete(*, prompt, source_text, timeout) -> dict` — транспорт модели (инжектится). Таймаут 30с обязателен каждый вызов.
- `extract(source_text) -> list[ExtractedCondition]` — max 1 retry со строгим промптом; валидация: JSON `{conditions:[...]}`, терм из 10, `quote ⊆ raw_text` при `value≠null`, `confidence∈[0,1]`; итоговая ошибка → `ManualInputRequired` (ручной ввод, не фейк).
- `transcribe(audio) / ocr(image)` — при отсутствии метода у клиента → `ManualInputRequired`.
- `draft_questions(registry)` — чистый код: только `conflict/unknown`.
- `draft_owner_message(qs)` — шаблон + `needs_manual_confirm=True`; отправки нет.
- `translate_kg(text)` — бонус; при неуверенности остаётся русская версия.

## Реальный API

- Статус: **не подтверждён** → `test_real_api_skipped_without_docs` = SKIP.
- После получения доки: дописать сюда имена моделей, лимиты аудио/фото, формат image input, structured JSON — отдельным коммитом + снять SKIP точечным тестом.
- Demo до тех пор: только «сохранённый результат» с явной меткой.
