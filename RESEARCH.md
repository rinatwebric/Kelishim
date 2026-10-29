# Skills для Muse Code и проект Kelishim

## Что проверено

Meta описывает Muse Code как terminal coding agent для планирования, написания и проверки кода. В официальной документации указаны встроенные background agents, автоматический fan-out с git worktrees, workflows, reviewer-проход, event log/replay, headless `muse exec` и режимы разрешений. Поэтому не нужно пытаться вручную воспроизводить мультиагентный orchestration через десятки промптов: проектные skills должны задавать доменные правила и критерии качества.

Muse Code имеет доступ к Muse Spark, Muse Wonder и Muse Image; для отдельной интеграции в приложение нужно сверять именно документацию хакатона и фактический API-контракт, а не предполагать, что CLI-возможность равна публичному API. В ТЗ это особенно важно для Voice Transcribe и строгого JSON-ответа.

Agent Skills — открытый формат: папка с обязательным `SKILL.md`, frontmatter `name`/`description`, инструкциями и опциональными `scripts/`, `references/`, `templates/`. Поддерживается progressive disclosure: агент сначала видит metadata, а полное тело загружает только при срабатывании. Подходящие места в репозитории — `.agents/skills/` или `.github/skills/`; конкретный путь для Muse Code следует подтвердить на установленной версии, поэтому рядом оставлен `AGENTS.md` как надёжный project-level fallback.

## Рекомендуемый набор

- `kelishim-spec-planner` — декомпозиция ТЗ, вертикальные срезы и acceptance tests.
- `kelishim-registry-core` — нормализация сумм/валют/сроков, статусы и обязательные pytest-кейсы.
- `kelishim-muse-integration` — адаптеры моделей, JSON validation, timeout/retry и ручной fallback.
- `kelishim-qa-demo` — мобильный UX, состояния, цитаты, smoke-flow и сценарий demo до 3 минут.
- `AGENTS.md` — постоянные правила проекта: ограничения продукта, стек, порядок работ и definition of done.

## Внешние источники

[1]: https://dev.meta.ai/products/muse-code "Meta Muse Code"
[2]: https://musecodes.io/docs/ "Muse Code CLI documentation"
[3]: https://github.com/agentskills/agentskills "Agent Skills specification"
[4]: https://agentskills.io/home "Agent Skills overview"
[5]: https://docs.github.com/en/copilot/concepts/customizations/agent-skills "GitHub Copilot Agent Skills"
[6]: https://github.com/supabase/agent-skills "Supabase Agent Skills"
[7]: https://github.com/awslabs/ai-skills "AWS reusable AI skills"
