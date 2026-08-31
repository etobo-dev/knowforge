# GitHub labels (etobo-tech/knowforge)

Canonical allowlist for issue labels. Agents and humans must **only** assign labels
from this file. Do **not** create new labels via the API or UI unless this list is
updated in the same change.

Create these labels in the GitHub repo settings (or via `gh label create`) before
first use.

## module::

| Label | Use for |
| --- | --- |
| `module::api` | `back/api/` routes, schemas, handlers |
| `module::back` | `back/` runtime outside `api/` and `rag/` (db, utils, lambda) |
| `module::rag` | `back/rag/` indexing, retrieval, agents |
| `module::front` | `front/` Next.js app |
| `module::infra` | `infra/` Terraform, deploy scripts |
| `module::cross` | Repo-wide: hooks, CI, `validate-commit.js`, `planning/` |
| `module::all` | Changes spanning multiple modules |

## milestone::

Planning backlog IDs from [`planning/MILESTONES.md`](../planning/MILESTONES.md). Add
when opening issues for active work only.

| Label | Phase |
| --- | --- |
| `milestone::M0.1` … `milestone::M0.9` | Phase 0 — Foundations |
| `milestone::M1.1` … `milestone::M1.10` | Phase 1 — KB agent beta |

Example: issue for `M0.1.1` → `milestone::M0.1` + `module::cross`.

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
| `status::done` | Shipped / closed |
| `status::cancelled` | Won't do |
| `status::blocked` | Waiting on dependency or decision |

## type::

| Label | When |
| --- | --- |
| `type::task` | Implementation slice from `MILESTONES.md` (default for dev work) |
| `type::feature` | User-facing capability (product) |
| `type::bug` | Incorrect behavior |
| `type::chore` | Tooling, deps, refactor with no behavior change |

## Flat allowlist

```text
module::api
module::back
module::rag
module::front
module::infra
module::cross
module::all
milestone::M0.1
milestone::M0.2
milestone::M0.3
milestone::M0.4
milestone::M0.5
milestone::M0.6
milestone::M0.7
milestone::M0.8
milestone::M0.9
milestone::M1.1
milestone::M1.2
milestone::M1.3
milestone::M1.4
milestone::M1.5
milestone::M1.6
milestone::M1.7
milestone::M1.8
milestone::M1.9
milestone::M1.10
priority::high
priority::medium
priority::low
status::idea
status::pending
status::doing
status::done
status::cancelled
status::blocked
type::task
type::feature
type::bug
type::chore
```
