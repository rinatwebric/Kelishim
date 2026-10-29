---
name: frontend-design
description: Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. Helps with aesthetic direction, typography, and making choices that don't read as templated defaults.
license: Complete terms in LICENSE.txt
---

# Frontend Design

Approach this as the design lead at a design studio known for giving every client a distinct visual identity that is not mistaken for anyone else's. This client has already rejected proposals that felt cliché or templated, and is paying for a distinctive point of view: make deliberate, opinionated choices about palette, typography, and layout that are specific to this brief, and take aesthetic risk if justified.

## Ground your designs in the subject matter

If the brief does not identify what the product or subject matter is, identify it yourself before designing, and confirm with the client. Subject industry, materials and vernacular are where distinctive choices come from.

## Design principles

Hero first: open with the most characteristic thing in the subject's world. Typography carries personality — one or two families, clearly distinct, deliberate type scale. Default line length <80 chars.

Avoid default tells: single-word accent in headline, ALL-CAPS labels everywhere, unnecessary eyebrows, numbered 01/02/03 markers for non-sequences, SaaS-card kit (identical rounded cards + same soft shadow + gradient wash), cream #F4F1EA + serif + terracotta #D97757 as default, near-black + acid accent as default, broadsheet hairlines as default regardless of brief.

Motion: one orchestrated moment, not scattered fade-slide on every section. Motion answering user action is welcome. Respect `prefers-reduced-motion`.

## Process: plan, review against the brief, build, critique

Two passes. First: compact token system (color 4-6 hex, type roles, layout concept + ASCII wireframe, principles). Then review plan against brief: if any part reads like generic default — revise, say what changed and why. Only then write code. Watch CSS specificity collisions.

Restraint: one memorable element, rest quiet. Quality floor without announcing: responsive to mobile, visible keyboard focus, reduced motion, accessible contrast, harmonious palette. Screenshot-critique if possible.

Copy: plain verbs, sentence case, active voice, CTA says what happens ("Save changes"), errors explain fix, empty states invite action.

## Kelishim binding

- Mobile-first 360-430px, no horizontal scroll, targets >=44px.
- Registry statuses always icon+word: ❓ Не указано / 🟡 Один источник / ✅ Совпадает / ⚠️ Противоречие.
- Quotes visible, low-confidence/hedged marked by text not color only.
- Legal disclaimer always visible (AGENTS.md).
- No purple-gradient AI slop; calm rental-registry aesthetic, Russian-language UI.

## Source

- Origin: `anthropics/skills` frontend-design (LICENSE.txt upstream)
- Fetched: 2026-10-29
- Reason: Kelishim Slice 4 UI direction
