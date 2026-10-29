---
name: web-interface-guidelines
description: Review UI code for Vercel Web Interface Guidelines compliance. Use when asked to review UI, check accessibility, audit design, or review UX.
---

# Web Interface Guidelines (Kelishim snapshot 2026-10-29)

Full source (fetch fresh before each review):

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

## Rules (snapshot)

### Accessibility

- Icon-only buttons need `aria-label`; form controls need label; images need alt; decorative icons `aria-hidden`.
- `<button>` for actions, `<a>`/`<Link>` for navigation, never `<div onClick>`.
- Keyboard handlers, semantic HTML first, hierarchical h1-h6, skip link, async updates `aria-live="polite"`.

### Focus / Forms / Animation / Typography

- Visible `focus-visible:ring`, never bare `outline:none`. Group focus `:focus-within`.
- Inputs: correct type/inputmode, autocomplete+name, clickable labels, inline errors + focus first error, placeholders end with … + example.
- Honor `prefers-reduced-motion`; animate transform/opacity only; never `transition:all`.
- `…` not `...`, curly quotes, `tabular-nums` for numbers, `text-wrap:balance/pretty` on headings.

### Content / Images / Performance / Nav / Touch / Layout

- Truncate/line-clamp/break-words; flex children `min-w-0`; empty states never broken.
- img width+height anti-CLS; lazy below fold; priority above fold.
- Virtualize lists >50; no layout reads in render; uncontrolled inputs preferred; preconnect CDN; font preload swap.
- URL reflects state (filters/tabs); destructive actions need confirm/undo.
- `touch-action:manipulation`; overscroll contain in modals; safe-area insets; no unwanted x-scroll; flex/grid over JS measurement.

### Anti-patterns

`user-scalable=no`, paste-blocking, `transition:all`, outline-none w/o replacement, div-onClick nav, images w/o dims, unlabeled inputs, hardcoded Intl formats, unjustified autoFocus, GIF over video, gesture-only actions.

## Output

Group by file, `file:line` terse. `✓ pass` if clean.

## Source

- Origin: `vercel-labs/web-interface-guidelines` (MIT presumed — check upstream)
- Snapshot: 2026-10-29
- Reason: Kelishim mobile 360-430px + a11y audit gate
