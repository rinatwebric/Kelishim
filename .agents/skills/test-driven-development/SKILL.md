---
name: test-driven-development
description: Use when implementing any feature or bugfix, before writing implementation code
---

# Test-Driven Development (TDD)

## Overview

Write the test first. Watch it fail. Write minimal code to pass.

**Core principle:** If you didn't watch the test fail, you don't know if it tests the right thing.

**Violating the letter of the rules is violating the spirit of the rules.**

## When to Use

**Always:**
- New features
- Bug fixes
- Refactoring
- Behavior changes

**Exceptions (ask your human partner):**
- Throwaway prototypes
- Generated code
- Configuration files

Thinking "skip TDD just this once"? Stop. That's rationalization.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over.

**No exceptions:**
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Don't look at it
- Delete means delete

Implement fresh from tests. Period.

## Red-Green-Refactor

### RED - Write Failing Test

Write one minimal test showing what should happen. One behavior, clear name, real code (no mocks unless unavoidable).

### Verify RED - Watch It Fail (MANDATORY)

Confirm test fails (not errors), failure message expected, fails because feature missing (not typos).

### GREEN - Minimal Code

Write simplest code to pass. Don't add features or over-engineer.

### Verify GREEN - Watch It Pass (MANDATORY)

Confirm test passes, other tests still pass, output pristine. Run full project suite (`pytest`, `npm test`), not just single file.

### REFACTOR - Clean Up

After green only: remove duplication, improve names, extract helpers. Keep tests green.

## Source

- Origin: `obra/superpowers` (MIT, presumed — verify LICENSE in upstream repo before commercial redistribution)
- Fetched: 2026-10-29 via raw.githubusercontent.com
- Reason: pytest verification / TDD gate for Kelishim Slice 1+
