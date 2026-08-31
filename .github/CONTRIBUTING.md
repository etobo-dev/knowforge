# Contributing — commits & issues

Conventions adapted from [noticrypt](https://github.com/etobo-tech/noticrypt) for Knowforge.
Enforced locally by `validate-commit.js` (see `.githooks/commit-msg`).

Planning context: [`planning/HANDOFF.md`](../planning/HANDOFF.md), [`planning/MILESTONES.md`](../planning/MILESTONES.md).

---

## Commits

### Header format

```text
<module>\<type>(<scope>): #<issue> <subject>
<module>\<type>(<scope>): #<issue>/<subtask> <subject>
```

| Part | Rule | Examples |
|------|------|----------|
| `module` | Area of the repo (see below) | `back`, `rag`, `cross` |
| `type` | Kind of change | `feat`, `fix`, `docs`, `test` |
| `scope` | Layer or concern | `back`, `front`, `ci`, `infra` |
| `issue` | GitHub issue number | `#12`, `#12/2` (optional subtask) |
| `subject` | Imperative, **lowercase**, no period | `add central config module` |

**Rules**

- Header + **blank line** + **non-empty body** (required).
- Max **100 characters** per line.
- `module`, `type`, `scope`, and `subject` are **lowercase**.
- Reference a real GitHub issue when one exists; for repo-only chores before issues exist, open a `type::chore` issue first or use the planning issue for the active milestone.

### Valid modules

| Module | Path / meaning |
|--------|----------------|
| `all` | Multiple modules in one commit |
| `api` | `back/api/` |
| `back` | `back/` except `api/` and `rag/` |
| `rag` | `back/rag/` |
| `front` | `front/` |
| `infra` | `infra/`, deploy scripts |
| `cross` | Hooks, CI, root config, `planning/`, `validate-commit.js` |

### Valid types

`feat` · `fix` · `docs` · `style` · `refac` · `perf` · `test` · `build` · `revert`

**Type = what kind of change.** Prefer `feat` / `fix` for behavior; use `docs` only when the
commit is **documentation-only** (no code). Repo workflow (hooks, templates, labels) is usually
`feat` or `fix`, not `docs`.

### Valid scopes

`chore` · `back` · `front` · `ci` · `infra` · `planning`

**Scope = where or what area** — not the same word as the type. Do **not** use `docs` as a scope
(it collides with the `docs` type). Do **not** write `docs(docs)`.

| You are changing… | Type | Scope | Example |
|-------------------|------|-------|---------|
| App / API code | `feat` / `fix` | `back`, `front`, `infra` | `back\feat(back): #15 add config module` |
| `planning/*.md` | `feat` / `docs` | `planning` | `cross\feat(planning): #3 add architecture diagrams` |
| `.github/`, hooks, `validate-commit.js` | `feat` / `fix` / `docs` | `chore` | `cross\feat(chore): #0 add issue templates` |
| GitHub Actions | `feat` / `fix` | `ci` | `cross\feat(ci): #0 add backend deploy workflow` |
| README / user-facing docs only | `docs` | `chore` or layer scope | `cross\docs(chore): rewrite root readme` |

### Body

- Explain **why** and meaningful **what** (behavior, trade-offs, limits).
- Do **not** paste a raw file list as the only content.
- Use bullets when scanning helps (migration notes, API surface, failure modes).
- Wrap code identifiers in backticks: `upload_document`, `DEV_USER_ID`, `planning/ROADMAP.md`.

### Examples

```text
cross\feat(chore): #0 add github commit and issue conventions

Document Knowforge contribution workflow adapted from noticrypt:
CONTRIBUTING guide, label allowlist, and task/bug issue templates.
```

```text
cross\feat(planning): #3 add architecture diagrams

Document target beta layout in planning/ARCHITECTURE.md so new sessions
do not depend on chat history.

- Links from HANDOFF and ROADMAP
- Mermaid: overview, ingest, chat SSE
```

```text
back\feat(back): #15 add central config module

Introduce `config/` package for quotas and model names per ROADMAP M0.1.1.
No behavior change until M0.1.2 wires existing reads.
```

```text
rag\fix(back): #42/1 guard empty multiquery results

When all three reformulations return zero nodes, return the standard
no-context reply instead of calling the LLM with an empty context.
```

### Setup hook

```bash
./scripts/setup-git-hooks.sh
```

---

## Issues (GitHub)

Repo: **etobo-tech/knowforge**. Labels: [`.github/LABELS.md`](./LABELS.md) only.

### When to open an issue

- **Active window:** only issues for the **current milestone** in [`planning/MILESTONES.md`](../planning/MILESTONES.md) (see HANDOFF §3).
- One issue ≈ one row in MILESTONES (`M0.1.1`, `M0.1.2`, …).
- Do not bulk-create the full backlog; open the next slice when the current milestone closes.

### Title format

```text
[<milestone-id>] <imperative short title>
```

| Kind | Pattern | Example |
|------|---------|---------|
| Milestone task | `[M0.1.1] …` | `[M0.1.1] Add central config module` |
| Bug | `[bug] …` | `[bug] Upload fails on duplicate hash` |
| Feature (product) | `[feature] …` | `[feature] Google Drive folder picker` |

Use the milestone ID from `MILESTONES.md` when the issue maps to a planned slice.

### Labels (typical)

| Work type | Labels |
|-----------|--------|
| M0.1.1 implementation | `type::task`, `module::cross`, `milestone::M0.1`, `status::pending`, `priority::medium` |
| API route change | `type::task`, `module::api`, `milestone::M0.x`, … |
| Production bug | `type::bug`, `module::<area>`, `priority::high`, `status::pending` |
| User-facing feature | `type::feature`, `module::<area>`, … |

Move `status::pending` → `status::doing` → `status::done` as you work.

### Templates

| Template | Use |
|----------|-----|
| [Task](./ISSUE_TEMPLATE/task.md) | Default — implementation from `MILESTONES.md` |
| [Bug report](./ISSUE_TEMPLATE/bug_report.md) | Incorrect behavior |
| [Feature request](./ISSUE_TEMPLATE/feature_request.md) | New product capability (not yet in milestones) |

### Issue body (task template)

Keep it short until implementation starts; expand acceptance criteria when picking up the issue.

Required sections: **Goal**, **Scope**, **Acceptance criteria**, **Verify**.

Link planning docs when relevant (`ROADMAP` §, `ARCHITECTURE` diagram).

### Closing issues

- Reference in commit: `#<issue>` in the header.
- PR description: `Closes #<issue>` when the PR fully completes the issue.

---

## Quick reference

```text
Commit:  back\feat(back): #15 add central config module
Issue:   [M0.1.1] Add central config module
Labels:  type::task, module::cross, milestone::M0.1, status::pending
```
