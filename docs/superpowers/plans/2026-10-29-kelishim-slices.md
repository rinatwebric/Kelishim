# Kelishim Vertical Slices Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Построить мобильный-first прототип реестра обещаний аренды: источники → извлечение → сравнение → вопросы → ответ → итог, проходящий demo за 3 минуты с телефона.

**Architecture:** Доменное ядро — чистый Python без LLM (нормализация + статусы кодом); тонкие Muse-адаптеры за интерфейсами с валидацией и ручным fallback; FastAPI + JSON/SQLite persistence; React+Vite+TS+Tailwind UI только вокруг состояний loading/error/success.

**Tech Stack:** Frontend React + Vite + TypeScript + Tailwind CSS; Backend Python + FastAPI; Persistence SQLite или JSON-файл на сделку; Tests pytest + Vitest/Testing Library.

**Spec:** `docs/spec.md` (отсутствует — создаётся в Task 0; до этого авторитет: `AGENTS.md` + `.agents/skills/kelishim-{spec-planner,registry-core,muse-integration,qa-demo}/SKILL.md`)

## Global Constraints

- Не определять мошенников, риск, право собственности или юридическую действительность договора.
- Не скрейпить сайты объявлений.
- Не отправлять сообщения хозяину автоматически.
- Каждое извлечённое значение хранить с точной цитатой из исходника.
- Если условие не упомянуто, возвращать `value: null`, не додумывать.
- Решение о совпадении/конфликте принимает код, не модель.
- Сбой модели должен приводить к ручному вводу, а не к белому экрану.
- Нельзя менять схему данных без отдельного решения владельца проекта.
- Схема фиксирована: `rent_amount, deposit, term, utilities, pets, prepayment, repairs, owner_access, termination, deposit_return`.
- На каждый вызов модели timeout 30 секунд, максимум 2 попытки невалидного JSON, fallback на ручной ввод.
- Не класть API-ключ во frontend и не коммитить `.env`.
- Язык интерфейса русский; кыргызский только бонус, не блокирует hero flow.
- Статусы с символом и словом: `❓ Не указано`, `🟡 Один источник`, `✅ Совпадает`, `⚠️ Противоречие`.
- Сообщение нельзя считать готовым без ручного подтверждения.
- Постоянная пометка: «Приложение помогает зафиксировать условия и показывает, что нужно уточнить. Это не юридическая консультация».
- Mobile 360–430 px без горизонтальной прокрутки; touch targets минимум 44 px; контраст AA.
- Работает без регистрации по публичной ссылке; перезагрузка сохраняет сделку; предусмотрено удаление данных.

## Review Focus

- Смешанные валюты `30 000 сом vs 500 USD` — разумный человек ждёт `conflict`, а не молчаливую конвертацию.
- Хеджированные формулировки «кажется 30к», «наверное можно с животными» — ждёт `single + needs_manual_check`, а не `match`.
- Пустой/мусорный вход в нормализацию — ждёт структурированную ошибку + сохранённый исходник, а не падение.
- Низкая уверенность `confidence < 0.6` без hedged — ждёт видимую текстовую метку, а не только цвет.
- `owner_reply` меняющий статус — ждёт пересчёт реестра кодом и видимое изменение иконки.

---

### Task 0: Восстановление `docs/spec.md` (блокер)

**Files:**
- Create: `docs/spec.md`
- Test: ручная сверка владельцем (approve в чате)

**Interfaces:**
- Consumes: `AGENTS.md`, `.agents/skills/kelishim-*/SKILL.md`, `START_HERE.md`
- Produces: FR-1—FR-8, схема 10 условий, hero-flow 3 мин, acceptance-критерии для Task 1–5

- [ ] **Step 1: Собрать черновик spec из AGENTS.md + 4 skills (FR-1—FR-8, 10 полей, статусы, timeout/retry, hero-flow, DoD) в `docs/spec.md`**
- [ ] **Step 2: Показать diff владельцу и получить explicit approve (схема считается замороженной только после approve)**
- [ ] **Step 3: Commit**

```bash
git add docs/spec.md
git commit -m "docs: restore spec FR-1-8 + frozen 10-field schema"
```

**Acceptance:** файл существует, владелец написал «approve spec».

---

### Task 1: Доменная схема + нормализация + статусы + pytest

**Files:**
- Create: `backend/domain/schema.py`, `backend/domain/normalize.py`, `backend/domain/registry.py`
- Create: `backend/tests/test_normalize.py`, `backend/tests/test_registry.py`
- Test: `pytest backend/tests -q`

**Interfaces:**
- Consumes: `docs/spec.md` (Task 0)
- Produces:
  - `ExtractedCondition(term, value, currency, quote, confidence: float[0..1], hedged: bool, needs_manual_check: bool, raw_text)`
  - `normalize_amount(str) -> (int | None, currency | None)` — `30 тыс/30 000/30к → 30000`; сом≠USD
  - `normalize_term(str) -> months: int | None`; `normalize_pets(str) -> yes/no/negotiable/unknown`
  - `compute_status(values: list) -> unknown/single/match/conflict`

- [ ] **Step 1: Write failing test `test_amount_variants` (30 тыс/30 000/30к → 30000)**
- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_normalize.py::test_amount_variants -v`
Expected: FAIL with "module not found / function not defined"

- [ ] **Step 3: Implement `normalize_amount` + `normalize_term` + `normalize_pets` в `backend/domain/normalize.py`**
- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_normalize.py -v`
Expected: PASS

- [ ] **Step 5: Write failing tests регистра: unknown/single/match/conflict, hedged→single+manual, 30к сом vs 500 USD→conflict, совпадение разных написаний→match, отсутствие цитаты→ошибка, confidence<0.6→needs_manual_check, owner_reply меняет статус**
- [ ] **Step 6: Run to verify they fail**

Run: `pytest backend/tests/test_registry.py -v`
Expected: FAIL

- [ ] **Step 7: Implement `compute_status` + проверка цитаты (`quote in raw_text`) в `backend/domain/registry.py` + `schema.py`**
- [ ] **Step 8: Run full suite + coverage**

Run: `pytest backend/tests -q`
Expected: PASS, все тесты зелёные. Доп.: `pytest --cov=backend/domain --cov-report=term` → 100% по домену.

- [ ] **Step 9: Commit**

```bash
git add backend/domain backend/tests
git commit -m "feat(domain): schema + normalize + registry statuses + tests"
```

**Acceptance:** `pytest backend/tests -q` зелёный; показать `git diff --stat`.

---

### Task 2: Muse adapter + contract tests (без выдуманных endpoint)

**Files:**
- Create: `backend/adapters/muse_adapter.py`, `backend/tests/test_muse_contract.py`, `docs/muse-contract.md`
- Test: `pytest backend/tests/test_muse_contract.py -v`

**Interfaces:**
- Consumes: `ExtractedCondition` из Task 1
- Produces: `transcribe(audio)->text`, `ocr(image)->text`, `extract(source_text)->list[ExtractedCondition]`, `draft_questions(registry)->list`, `draft_owner_message(qs)->str`, `translate_kg(text)->str`; все с `timeout=30`, retry×1, fallback `ManualInputRequired`

- [ ] **Step 1: Write failing contract test `test_extract_contract_validates_quote_and_confidence` (мок клиента, проверка quote⊆raw_text, confidence∈[0,1], null-допуск, retry×1, timeout=30)**
- [ ] **Step 2: Run to verify it fails**

Run: `pytest backend/tests/test_muse_contract.py -v`
Expected: FAIL (adapter missing)

- [ ] **Step 3: Сверка с докой хакатона (модели, лимиты аудио/фото, image input, structured JSON) → зафиксировать реальные имена в `docs/muse-contract.md`. Если доки нет — адаптер с injectable-клиентом, тесты `skipped` с причиной, hero flow идёт через «сохранённый результат» с меткой**
- [ ] **Step 4: Implement `muse_adapter.py` строго по `docs/muse-contract.md`; валидация JSON; ошибка → понятный текст + ручной ввод, никаких фейковых успехов**
- [ ] **Step 5: Run contract tests**

Run: `pytest backend/tests/test_muse_contract.py -v`
Expected: PASS или честный SKIP с причиной

- [ ] **Step 6: Commit**

```bash
git add backend/adapters backend/tests/test_muse_contract.py docs/muse-contract.md
git commit -m "feat(muse): adapter + contract tests, manual fallback"
```

**Acceptance:** нет выдуманных endpoint; любой сбой ведёт к ручному вводу.

---

### Task 3: Persistence + API минимум для hero flow

**Files:**
- Create: `backend/app.py` (FastAPI), `backend/store.py` (JSON/SQLite)
- Create: `backend/tests/test_api_flow.py`
- Test: `pytest backend/tests/test_api_flow.py -v`

**Interfaces:**
- Consumes: Task 1–2
- Produces: `POST /deals`, `POST /deals/{id}/sources`, `POST /deals/{id}/owner_reply`, `GET /deals/{id}/registry`; персист survives restart; `DELETE /deals/{id}`

- [ ] **Step 1: Write failing test `test_two_sources_plus_owner_reply_recomputes_registry`**
- [ ] **Step 2: Run to verify it fails**

Run: `pytest backend/tests/test_api_flow.py -v`
Expected: FAIL

- [ ] **Step 3: Implement app+store; пересчёт реестра кодом после каждого source включая owner_reply**
- [ ] **Step 4: Run suite**

Run: `pytest backend/tests -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app.py backend/store.py backend/tests/test_api_flow.py
git commit -m "feat(api): deal persistence + registry recompute"
```

**Acceptance:** сделка без регистрации, переживает рестарт, удаляется.

---

### Task 4: UI mobile-first + demo-flow

**Files:**
- Create: `frontend/` (Vite+TS+Tailwind): старт, источники, реестр, цитата, вопросы, редактор сообщения + чекбокс подтверждения, owner_reply, итог
- Test: `npm run dev` + Playwright smoke 360–430px (`webapp-testing`, `web-interface-guidelines`)

**Interfaces:**
- Consumes: API Task 3
- Produces: экраны с loading/empty/error/success на каждое действие; иконка+слово статусов; цитаты раскрываются; сообщение заблокировано до ручного подтверждения; юр.оговорка всегда видна

- [ ] **Step 1: Scaffold Vite+TS+Tailwind + токены (frontend-design) + safe-area + 44px targets**
- [ ] **Step 2: Экран сделки: старт → «Попробовать на примере» → источники с прогрессом → реестр 4 статуса → цитата → вопросы только conflict/unknown → edit → подтвердить → owner_reply → пересчёт → итог**
- [ ] **Step 3: Smoke 360×800 и 430×900: нет x-scroll, все состояния достижимы, перезагрузка сохраняет**
- [ ] **Step 4: Design review (`web-design-reviewer` + `web-interface-guidelines`): `file:line` findings → fix pass**
- [ ] **Step 5: Commit**

```bash
git add frontend
git commit -m "feat(ui): mobile-first hero flow 360-430"
```

**Acceptance (3 мин с телефона):** старт → пример → реестр с 4 статусами → цитата → вопрос → edit+подтвердить → owner_reply → итог + оговорка видна.

---

### Task 5: QA / релиз

**Files:**
- Create: `README.md` (запуск, архитектура, ограничения, real vs saved demo, команды тестов), `evals/` (3–5 обезличенных образцов)
- Test: `pytest -q` + `npm run build` + smoke

**Interfaces:**
- Consumes: Task 0–4
- Produces: таблица эталон/верно/пропущено/ошибочно; честные известные ошибки; публичная ссылка без регистрации

- [ ] **Step 1: Собрать eval-таблицу, прогнать demo-образец полным циклом**
- [ ] **Step 2: README + cleanup `.env` из истории**
- [ ] **Step 3: Финальный прогон `pytest -q`, `npm run build`, smoke → push `main`, deploy на публичный URL**
- [ ] **Step 4: Commit**

```bash
git add README.md evals
git commit -m "docs: README + evals + release notes"
```

**Acceptance:** DoD из AGENTS.md закрыт.

---

## Self-Review

1. Spec coverage: FR извлечения/нормализации/статусов→Task 1; адаптеры→Task 2; персист/API→Task 3; UI/demo→Task 4; QA/DoD→Task 5; spec-блокер→Task 0. ✅
2. Step scan: каждый шаг — одно действие + проверка; без «обработать edge cases». ✅
3. Type consistency: `ExtractedCondition` определён раз в Task 1, далее только потребляется. ✅
4. Review Focus: 5 строк выше, каждая привязана к тесту Task 1 (`hedged`, `confidence`, мусорный вход, валюты, owner_reply). ✅
5. Proportion: план короче кода, тел функций нет — только сигнатуры и ассёрты. ✅
