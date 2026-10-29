---
name: web-design-reviewer
description: 'This skill enables visual inspection of websites running locally or remotely to identify and fix design issues. Triggers on requests like "review website design", "check the UI", "fix the layout", "find design problems". Detects issues with responsive design, accessibility, visual consistency, and layout breakage, then performs fixes at the source code level.'
---

# Web Design Reviewer (Kelishim proxy)

## Scope

Static sites, React/Vue/Next.js, Tailwind/CSS. Kelishim: React+Vite+TS+Tailwind, mobile-first 360-430px.

## Prerequisites

Target URL running (localhost/staging), browser automation (Playwright `webapp-testing`), source access for fixes.

## Workflow

1. Information gathering: confirm URL, detect framework (package.json/vite.config/tailwind.config), styling method, scope.
2. Visual inspection: traverse pages, screenshot, DOM snapshot. Check layout overflow/overlap, responsive 375/768/1280/1920 (Kelishim: focus 360-430), contrast, focus states, alt text, font/color/spacing consistency. Use `web-interface-guidelines` rules.
3. Fix: prioritize P1 functional > P2 UX > P3 polish. Minimal diffs, respect existing patterns. One issue at a time.
4. Re-verify: reload/HMR, before/after screenshots, regression check. >3 attempts on one issue → ask user.

## Output

Summary table (URL/framework/styling/viewports/issues found/fixed), per-issue P1/P2 blocks with file:line + fix, unfixed with reason, recommendations.

Full workflow upstream:

```
https://github.com/github/awesome-copilot/tree/main/skills/web-design-reviewer
```

References there: `references/visual-checklist.md`, `references/framework-fixes.md` — скачать перед Slice 4 при нужде.

## Source

- Origin: `github/awesome-copilot` web-design-reviewer
- Fetched proxy: 2026-10-29
- Reason: Kelishim Slice 4 design QA loop
