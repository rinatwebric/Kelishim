---
name: vercel-react-best-practices
description: React and Next.js performance optimization guidelines from Vercel Engineering. This skill should be used when writing, reviewing, or refactoring React/Next.js code to ensure optimal performance patterns. Triggers on tasks involving React components, Next.js pages, data fetching, bundle optimization, or performance improvements.
license: MIT
metadata:
  author: vercel
  version: "1.0.0"
---

# Vercel React Best Practices (proxy)

Comprehensive performance optimization guide for React and Next.js — 70 rules across 8 categories.

## When to Apply

- Writing new React components or Next.js pages
- Implementing data fetching
- Reviewing code for performance issues
- Refactoring React code (Kelishim Slice 4)
- Optimizing bundle size or load times

## Rule Categories by Priority

| Priority | Category | Impact |
|----------|----------|--------|
| 1 | Eliminating Waterfalls | CRITICAL |
| 2 | Bundle Size Optimization | CRITICAL |
| 3 | Server-Side Performance | HIGH |
| 4 | Client-Side Data Fetching | MEDIUM-HIGH |
| 5 | Re-render Optimization | MEDIUM |
| 6 | Rendering Performance | MEDIUM |
| 7 | JavaScript Performance | LOW-MEDIUM |
| 8 | Advanced Patterns | LOW |

Full rules live upstream (70 files). Перед Slice 4 скачать полностью:

```
https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices
```

Key rules для Kelishim mobile-first:
- `bundle-dynamic-imports`, `bundle-barrel-imports`, `bundle-defer-third-party`
- `rendering-content-visibility`, `rendering-hoist-jsx`
- `client-localstorage-schema` (персист сделки)
- `rerender-*` (дешёвые ре-рендеры реестра)

## Source

- Origin: `vercel-labs/agent-skills` MIT
- Fetched proxy: 2026-10-29
- Reason: Kelishim frontend performance, mobile 360-430px
