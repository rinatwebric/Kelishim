---
name: web-design-guidelines
description: Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".
metadata:
  author: vercel
  version: "1.0.0"
---

# Web Interface Guidelines (proxy)

Review files for compliance with Web Interface Guidelines.

## How It Works

1. Fetch the latest guidelines before each review:

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in the fetched guidelines
4. Output findings in terse `file:line` format

## Usage in Kelishim

- Slice 4 QA: проверить 360-430px без горизонтальной прокрутки, touch targets ≥44px, контраст AA, иконка+слово для статусов, цитаты видны, юр.оговорка всегда видна.
- Если файлов нет — спросить какие файлы ревьюить.

## Source

- Origin: `vercel-labs/agent-skills` MIT + `vercel-labs/web-interface-guidelines`
- Fetched proxy: 2026-10-29
- Reason: mobile UX review + accessibility audit для Kelishim
