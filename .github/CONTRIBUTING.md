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
| `module` | Deployable area (see below) | `api`, `ingest`, `chat`, `cross` |
| `type` | Kind of change | `feat`, `fix`, `docs`, `test` |
| `scope` | Layer or concern | `back`, `front`, `ci`, `infra` |
| `issue` | GitHub issue number | `#12`, `#12/2` (optional subtask) |
| `subject` | Imperative, **lowercase**, no period | `add central config module` |

**Rules**

- Header + **blank line** + **non-empty body** (required).
- Max **100 characters** per line.
- `module`, `type`, `scope`, and `subject` are **lowercase**.
- Reference a real GitHub issue when one exists; for repo-only work before issues exist, use `#0` or open a `type::task` issue in the active milestone window.

### Valid modules

Deployable microservices (target layout; migration from monolithic `back/` is gradual).

| Module | Path / deploy | Meaning |
|--------|----------------|---------|
| `all` | Multiple modules | One commit/issue spans API + Ingest + Chat, etc. |
| `api` | `api/` (today `back/api/` + DB) | REST handlers, Postgres, authz, quotas, enqueue jobs |
| `ingest` | `ingest/` (today `back/rag/` indexing) | Sources, extract/index graph, embeddings, vector upsert |
| `chat` | `chat/` (today `back/rag/` query) | Chat graph, retrieval, SSE streaming, message persist |
| `front` | `front/` | Next.js app |
| `infra` | `infra/` | Terraform, deploy scripts |
| `cross` | Repo-wide | Shared config, CI, hooks, `planning/`, `validate-commit.js` |

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
| Service code | `feat` / `fix` | `back`, `front`, `infra` | `api\feat(back): #15 add workspace filter` |
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
cross\feat(back): #15 add central config module

Introduce shared config for quotas and model names. No behavior change
until a follow-up issue wires existing reads.
```

```text
chat\fix(back): #42 guard empty multiquery results

When all three reformulations return zero nodes, return the standard
no-context reply instead of calling the LLM with an empty context.
```

### Setup hook

```bash
./scripts/setup-git-hooks.sh
```

---

## Issues (GitHub)

Repo: **etobo-dev/knowforge**. Labels: [`.github/LABELS.md`](./LABELS.md) only.

### When to open an issue

- **Active window:** only issues for the **current milestone** in [`planning/MILESTONES.md`](../planning/MILESTONES.md) (see HANDOFF §3).
- One issue ≈ one row in [`planning/MILESTONES.md`](../planning/MILESTONES.md).
- Assign the GitHub **Milestone** field to the planning milestone (e.g. `M0.1 — Central configuration`). Do **not** put the milestone in the title or body.
- Do not bulk-create the full backlog; open the next slice when the current milestone closes.

### Title format

Like [noticrypt](https://github.com/etobo-tech/noticrypt): **module prefix in brackets**, imperative title.

```text
[Module] <imperative short title>
```

| Kind | Pattern | Example |
|------|---------|---------|
| Task | `[API] …` | `[API] Verify Cognito JWT on requests` |
| Task | `[Ingest] …` | `[Ingest] Enqueue ingest job on upload` |
| Task | `[Cross] …` | `[Cross] Add central config module` |
| Bug | `[Module] …` | `[API] Upload fails on duplicate hash` |
| Feature (product) | `[Module] …` | `[Ingest] Google Drive folder picker` |

Use the **Mod** column in `MILESTONES.md` for the bracket tag. Title text = **Title** column in the same row.

### Labels (typical)

Pick labels only from [`.github/LABELS.md`](./LABELS.md). Use **one** `audience::` label per issue.

| Work type | Labels |
|-----------|--------|
| Milestone task (default) | `type::task`, `module::<area>`, `audience::engineering`, `status::pending`, `priority::medium` |
| API route change | `type::task`, `module::api`, `audience::engineering`, … |
| Production bug | `type::bug`, `module::<area>`, `audience::users`, `priority::high`, `status::pending` |
| User-facing feature (not in milestones) | `type::feature`, `module::<area>`, `audience::product` or `audience::users` |
| Accepted tech debt | `type::task`, `module::<area>`, `audience::engineering`, `status::controlled-technical-debt` |
| Stale / obsolete issue | `status::expired` (then close) |

Move `status::pending` → `status::doing` → close issue when shipped.

### Templates

| Template | Use |
|----------|-----|
| [Feature request](./ISSUE_TEMPLATE/feature_request.md) | Default — milestone slices from `MILESTONES.md` and net-new product ideas |
| [Bug report](./ISSUE_TEMPLATE/bug_report.md) | Incorrect behavior |

### Issue body (feature request template)

Use for milestone work and product features. Keep it short until implementation starts; expand the success checklist when picking up the issue.

Fill **What does success look like, and how can we measure that?** with measurable checkboxes. **Every box must be checked before closing the issue.**

Link planning docs when relevant (`ROADMAP` §, `ARCHITECTURE` diagram, `MILESTONES.md` row).

### Closing issues

- All items in **What does success look like, and how can we measure that?** must be checked.
- Reference in commit: `#<issue>` in the header.
- PR description: `Closes #<issue>` when the PR fully completes the issue.

---

## Quick reference

```text
Commit:    cross\feat(back): #15 add central config module
Issue:     [Cross] Add central config module
Milestone: M0.1 — Central configuration   (GitHub milestone field only)
Labels:    type::task, module::cross, audience::engineering, status::pending
```
