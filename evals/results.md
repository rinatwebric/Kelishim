# Eval-результаты (2026-10-29, доменное ядро, без модели)

Прогон: `PYTHONPATH=. python evals/run.py`

| sample | эталон | получено | итог |
|---|---|---|---|
| sample-01-zalog-conflict | deposit=conflict, rent=match | deposit=conflict, rent=match | ВЕРНО |
| sample-02-single-unknown | pets=unknown, rent=single, term=single | так же | ВЕРНО |
| sample-03-hedged-manual | pets=single, rent=match | так же | ВЕРНО |

Итого: 3/3 образцов сошлись.

## Известные честные ограничения

1. Большинство голосов не разрешает конфликт: `[30000, 35000, 30000]` → `conflict` (приоритет противоречию, см. Task 3 ruling). Разрешение — только правкой/удалением устаревшего источника, такого endpoint пока нет.
2. Валюты без конвертации: `(30000, KGS)` vs `(30000, USD)` → `conflict`. Курс не знаем и не выдумываем.
3. Отсутствующая валюта совместима с любой: `(30000, null)` vs `(30000, KGS)` → `match`. Допущение зафиксировано тестом.
4. Качество извлечения моделью (quote/confidence) измеряется только contract-тестами на моках — реальный API не подтверждён (`test_real_api_skipped_without_docs`).
