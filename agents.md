# Agent Working Rules

## Core Engineering Principles

- Always apply Clean Code principles.
- Keep code concise, readable, and maintainable.
- Use strong typing whenever the language/tooling supports it.
- Avoid unnecessary comments; only add comments when they provide real value.
- Prefer command-based setup (CLI) for scaffolding/configuration to reduce manual errors.

## Language and Writing Standards

- All code, comments, logs, and technical documentation must be written in English.

## Package Managers and Tooling

- Python work must always use `uv` as the package and environment manager.
- Frontend work must always use `pnpm` as the package manager.

## API and Function Design

- Functions must be called with named arguments whenever possible.
- Design code in a modular way and apply the Single Responsibility Principle (SRP) across the entire codebase, including backend, APIs, and frontend components.

## Delivery Process

- Work in micro-changes (small, incremental steps).
- Review changes before each commit.
- After each commit, re-check status and confirm before continuing with the next micro-change.

### Commit messages

- Follow [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md) (enforced by `validate-commit.js`).
- Header: `<module>\<type>(scope): #<issue> <subject>` — body required, max 100 chars/line, lowercase subject.
- Body must explain **why** and meaningful **what**; use bullets when helpful; backtick code identifiers.

### Issues

- Follow [`.github/CONTRIBUTING.md`](.github/CONTRIBUTING.md) and [`.github/LABELS.md`](.github/LABELS.md).
- Open issues only for the **active milestone window** (see [`planning/HANDOFF.md`](planning/HANDOFF.md)).
- Default template: **Task** with title `[M0.x.y] …`.

## Repository Awareness

- Always account for existing repository resources such as:
  - agent skills
  - issue templates
  - supporting documentation and helper files

## Persistent Memory

- Use Engram to read and store persistent memory across agent sessions when relevant.
