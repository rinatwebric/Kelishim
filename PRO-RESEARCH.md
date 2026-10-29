# Профессиональная система AI-разработки для Kelishim

## Главный вывод

Нет единого полного списка skills. Сильные команды используют не один огромный prompt, а несколько уровней:

1. **Project instructions** — постоянные правила проекта: `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.cursor/rules/*.mdc`.
2. **Skills** — небольшие on-demand процедуры с `SKILL.md`, скриптами, reference-файлами и тестами.
3. **Workflows** — цепочки skills и ролей: research → spec → implement → review → release.
4. **MCP/tools** — доступ к внешним системам: API, БД, issue tracker, документация, staging.
5. **Quality gates** — тесты, evals, contract checks, mobile smoke-flow, code review и security checks.

Большой universal skill обычно хуже: он перегружает контекст, смешивает разные задачи и чаще приводит к красивому, но непроверенному коду.

## Что обязательно добавить к текущему пакету

### 1. `lease-extraction` — извлечение условий

Извлекает из текста, фото или PDF: срок, аренду, депозит, коммунальные платежи, животных, ремонт, доступ владельца, расторжение и возврат залога. Каждое значение обязано иметь цитату, provenance, confidence и список неоднозначностей.

Активируется при загрузке нового источника. Нельзя додумывать отсутствующее условие.

### 2. `lease-normalization` — нормализация

Приводит суммы, валюты, даты, сроки и варианты «да/нет/по договорённости» к канонической JSON/Pydantic-схеме. Это должен быть отдельный детерминированный модуль, а не часть prompt модели.

### 3. `status-review` — статусы и ручная проверка

Фиксирует state machine: `received → extracting → needs_review → normalized → approved/failed`. Проверяет допустимые переходы, повторный запуск, идемпотентность и audit trail.

### 4. `extract-to-review` — главный workflow

Цепочка:

```text
источник → извлечение → проверка цитаты → нормализация → статус → ручное подтверждение
```

Это должен быть основной сценарий приложения, а не один большой запрос к AI.

### 5. `verification` — проверка приложения

Запускает backend tests, API contract tests, frontend lint/typecheck/tests, mobile viewport smoke и проверяет loading/error/empty/retry-состояния.

### 6. `kelishim-release-verify` — проверка релиза

Проверяет чистое окружение, миграции, health endpoint, frontend build, полный hero flow и возможность отката. Deployment и production write-операции должны требовать подтверждения.

### 7. `muse-api-integration` — интеграция Muse

Отдельный skill для auth, таймаутов, retry/backoff, rate limits, idempotency, ошибок и contract tests. Конкретные endpoint names, MCP tools и пути конфигурации нельзя выдумывать — их нужно подтвердить официальной документацией Muse.

### 8. `schema-and-migration` — схема и миграции

Любое изменение `Deal`, `Source`, `ExtractedCondition`, `RegistryRow` должно идти через schema review, миграцию, тесты и проверку обратной совместимости.

### 9. `mobile-ux-review` — мобильный UX

Проверяет 360—430 px, кнопки от 44 px, accessibility, прогресс обработки, ручной fallback, цитаты, ошибки и отсутствие горизонтальной прокрутки.

### 10. `research-to-spec-to-tickets` — работа по спецификации

Для каждой новой функции: исследование → уточнённая спецификация → acceptance criteria → небольшие tickets → реализация. Это резко лучше команды «сделай всё приложение».

### 11. `implement-and-review` — TDD и ревью

Процесс:

```text
тест поведения → минимальная реализация → зелёные тесты → рефакторинг → review diff
```

Review должен идти по двум осям:

- соответствует ли код стандартам проекта;
- соответствует ли исходному ТЗ.

### 12. `lease-quality-eval` — eval-набор

Набор из 3—5 обезличенных примеров и edge cases:

- разные обозначения валют;
- «30к», «30 тысяч», «30000 сом»;
- пропущенные условия;
- OCR-ошибки;
- кыргызско-русская смесь;
- неуверенные формулировки;
- противоречия между источниками.

Для каждой версии модели или prompt фиксировать правильные, пропущенные и ошибочные поля.

### 13. `adr-and-retro` — архитектурные решения

Записывает, почему выбраны SQLite/JSON/Supabase, как устроены adapters Muse, почему статусы вычисляются кодом и какие ограничения обнаружены во время demo.

## Что является skill, а что нет

**Skill** — повторяемая процедура с триггером и проверяемым результатом. Например: `lease-extraction`.

**Project instruction** — постоянное правило. Например: «не хранить API-ключ во frontend».

**Workflow** — цепочка действий. Например: `extract-to-review`.

**MCP** — внешний инструментальный слой. Например: вызов API, БД или issue tracker.

**Eval** — проверка качества процедуры или модели. Например: golden dataset по договорам.

## Рекомендуемая структура репозитория

```text
AGENTS.md
CLAUDE.md                         # если используется Claude Code
.cursor/rules/                    # если используется Cursor
.github/copilot-instructions.md   # если используется Copilot

.agents/skills/
  lease-extraction/SKILL.md
  lease-normalization/SKILL.md
  status-review/SKILL.md
  extract-to-review/SKILL.md
  verification/SKILL.md
  muse-api-integration/SKILL.md
  schema-and-migration/SKILL.md
  mobile-ux-review/SKILL.md
  lease-quality-eval/SKILL.md
  kelishim-release-verify/SKILL.md

backend/
frontend/
docs/spec.md
docs/agents/domain.md
docs/adr/
evals/evals.json
evals/fixtures/
evals/results/
scripts/
```

Один каталог `.agents/skills` можно сделать каноническим, а для конкретных агентов добавлять адаптеры. Нельзя считать, что Muse Code автоматически поддерживает все каталоги других агентов: это нужно проверить отдельно.

## Как применять skills в Muse Code

1. Сначала дать агенту `AGENTS.md` и ТЗ.
2. Попросить read-only аудит репозитория.
3. Затем попросить создать доменную схему и тесты нормализации.
4. После этого реализовать extraction adapter.
5. Только затем строить UI вокруг реальных loading/error/success-состояний.
6. После каждого вертикального среза запускать tests и smoke-flow.
7. Перед релизом просить отдельный spec-аудит и технический review.

Первый хороший запрос:

> Прочитай AGENTS.md, docs/spec.md и .agents/skills. Сначала проведи read-only аудит проекта. Не пиши код. Покажи текущий стек, работающие части, пробелы hero flow и рискованные места. Затем составь план вертикальных срезов с acceptance tests. После моего подтверждения начни только с доменной схемы и тестов нормализации/статусов.

## Профессиональные источники

[1]: https://github.com/agentskills/agentskills "Agent Skills Open Standard"
[2]: https://raw.githubusercontent.com/agentskills/agentskills/main/docs/skill-creation/best-practices.mdx "Agent Skills best practices"
[3]: https://raw.githubusercontent.com/agentskills/agentskills/main/docs/skill-creation/evaluating-skills.mdx "Agent Skills evaluation"
[4]: https://github.com/anthropics/skills "Anthropic Skills"
[5]: https://docs.anthropic.com/en/docs/claude-code/skills "Claude Code skills"
[6]: https://github.com/supabase/agent-skills "Supabase Agent Skills"
[7]: https://github.com/awslabs/ai-skills "AWS Labs AI Skills"
[8]: https://github.com/github/awesome-copilot "GitHub Awesome Copilot"
[9]: https://github.com/mattpocock/skills "Matt Pocock Skills"
[10]: https://developers.openai.com/codex/build-skills "OpenAI Codex skills"
[11]: https://developers.openai.com/codex/agent-configuration/agents-md "OpenAI Codex AGENTS.md"
[12]: https://developers.openai.com/codex/mcp "OpenAI Codex MCP"
[13]: https://cursor.com/docs/rules "Cursor rules"
[14]: https://cursor.com/docs/skills "Cursor skills"
[15]: https://cursor.com/docs/mcp "Cursor MCP"
[16]: https://cursor.com/learn/reviewing-testing "Cursor testing and review"
