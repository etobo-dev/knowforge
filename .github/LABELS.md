# GitHub labels (etobo-dev/knowforge)

Canonical allowlist for issue labels. Agents and humans must **only** assign labels
from this file. Do **not** create new labels via the API or UI unless this list is
updated in the same change.

Create these labels in the GitHub repo settings (or via `gh label create`) before
first use.

## module::

Deployable microservices + repo-wide. Match the `[Module]` prefix in issue titles.

| Label | Use for |
| --- | --- |
| `module::api` | REST API, Postgres access, authz, quotas, job enqueue (`api/`, today `back/api/` + `db/`) |
| `module::ingest` | Sources, extract/index graph, embeddings, vector upsert (`ingest/`, today `back/rag/` indexing) |
| `module::chat` | Chat graph, retrieval, SSE streaming (`chat/`, today `back/rag/` query) |
| `module::front` | `front/` Next.js app |
| `module::infra` | `infra/` Terraform, deploy scripts |
| `module::cross` | Shared config, CI, hooks, `planning/`, multi-module repo work |

## audience::

Who the issue is primarily for (adapted from [noticrypt](https://gitlab.com/elverytr/noticrypt/-/labels)).
Pick **one** per issue.

| Label | When |
| --- | --- |
| `audience::engineering` | Implementation, infra, refactors (default for milestone tasks) |
| `audience::product` | Product decisions, UX, roadmap, feature requests |
| `audience::users` | End-user-visible bugs or capabilities |

## priority::

| Label | When |
| --- | --- |
| `priority::high` | Blocks release, prod broken, security |
| `priority::medium` | Active milestone work (default) |
| `priority::low` | Nice-to-have, polish |

## status::

| Label | When |
| --- | --- |
| `status::idea` | Not scheduled |
| `status::pending` | Ready to pick up |
| `status::doing` | In progress |
| `status::blocked` | Waiting on dependency or decision |
| `status::cancelled` | Won't do (close with this label when applicable) |
| `status::expired` | No longer relevant (time or context) |
| `status::controlled-technical-debt` | Known debt accepted on purpose; track and revisit |

Closed issues do not need a `status::done` label — use GitHub **Close issue**.

## type::

| Label | When |
| --- | --- |
| `type::task` | Implementation slice from `MILESTONES.md` (default for dev work) |
| `type::feature` | User-facing capability (product), not yet in milestones |
| `type::bug` | Incorrect behavior |

Planning milestone → GitHub **Milestone** field only (e.g. `M0.1 — Central configuration`).
Do **not** duplicate milestones as labels.

Example: `[Cross] Add central config module` → Milestone field `M0.1 — Central configuration`,
labels `module::cross` + `type::task` + `audience::engineering` + `status::pending`.

## Flat allowlist

```text
module::api
module::ingest
module::chat
module::front
module::infra
module::cross
audience::engineering
audience::product
audience::users
priority::high
priority::medium
priority::low
status::idea
status::pending
status::doing
status::blocked
status::cancelled
status::expired
status::controlled-technical-debt
type::task
type::feature
type::bug
```
