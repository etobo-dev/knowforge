# Knowforge — Agent / Contributor Handoff

**Purpose:** Continue Knowforge work in a **new chat or another agent** without depending on prior conversation history.  
**Last design freeze:** ROADMAP **rev 3** (quotas = abuse caps only; SSE = Lambda Function URL; no billing product in beta).

If you are an AI agent: read this file first, then follow the reading order below. Do **not** invent a parallel roadmap.

---

## 1. Reading order

| Order | Doc | Why |
|------:|-----|-----|
| 1 | [`planning/HANDOFF.md`](./HANDOFF.md) (this file) | Process, active window, permission defaults, what not to do |
| 2 | [`planning/ROADMAP.md`](./ROADMAP.md) | Product vision, locked architecture, phases, non-goals |
| 3 | [`planning/MILESTONES.md`](./MILESTONES.md) | Ordered milestone/issue backlog (titles + one-liners) |
| 4 | [`planning/ARCHITECTURE.md`](./ARCHITECTURE.md) | Architecture diagrams (overview, flows, data model) |
| 5 | [`.github/CONTRIBUTING.md`](../.github/CONTRIBUTING.md) | Commit and issue conventions |
| 6 | [`AGENTS.md`](../AGENTS.md) | Repo engineering rules (`uv`, `pnpm`, SRP, English docs) |
| 7 | Code under `back/`, `front/`, `infra/`, `config/` | Current implementation (still LlamaIndex-era in places) |

Optional: `front/AGENTS.md` for Next.js-specific notes.

---

## 2. Current status

| Item | State |
|------|--------|
| Product design | Documented and self-reviewed (**ROADMAP rev 3**) |
| Milestone backlog | Draft in `MILESTONES.md` (north star, **not** all opened on GitHub) |
| Implementation of Phase 0+ | **Not started** as of this handoff |
| **Next work** | **M0.1 — Central configuration** (`[Cross] Add central config module` then `[Cross] Point existing code at central config`) |
| External beta | End of **Phase 1** / milestone **M1.10** |

---

## 3. How planning maps to GitHub (important)

- **`ROADMAP.md` + `MILESTONES.md` = north star** in the repo. Easy to consult; details may change.
- **Do not create all ~19 milestones / ~71 issues on GitHub at once.** That over-commits to a future that will drift.
- **GitHub active window (rule):**
  - At most **1 open milestone** (set on each issue via GitHub **Milestone** field — not in title or body)
  - About **≤5–8 open issues**
  - Issue titles: `[Module] …` per `MILESTONES.md` **Mod** column (e.g. `[API] Verify Cognito JWT on requests`)
  - When a milestone closes → open the **next** one from `MILESTONES.md` and expand issue bodies only as needed
- Phase **2** and **3** stay **outline-only** in markdown until Phase 1 / beta is done. **Do not implement them now.**

---

## 4. Delivery rules (must follow)

1. **Always ship a working product** — no big-bang rewrites.
2. **Atomic order** — finish issue N before N+1; finish milestone M before M+1 (see `MILESTONES.md`).
3. **Local first** — implement and test locally; when possible, wire into the **parent/production flow** and only push if nothing breaks.
4. **Cutover then delete** — when new logic fully replaces old, disconnect and **delete** legacy (no long dual stacks). Target end-state: **no LlamaIndex**.
5. **Abstractions** — prefer interfaces (Source, JobRunner, SecretStore, Retriever, Tracer, RateLimiter, LLM providers).
6. **Central config** — quotas, models, retention, etc. in centralized config, not scattered magic numbers.
7. **Micro-changes** — small commits; English for code/docs (`AGENTS.md`).
8. **Tooling** — Python: `uv`; frontend: `pnpm`.

---

## 5. Product snapshot (do not contradict)

- **SaaS multi-tenant:** Organization + Workspace from day one.
- **ACL = workspace (not per-file).** Default **public** workspace: all **org members** access implicitly. **Private** workspaces: explicit membership; create = org owner/admin.
- **Auth:** Cognito = AuthN (Google-first). AuthZ = app DB (roles/permissions). No Cognito Groups as product RBAC.
- **Chat:** One chat ↔ one workspace. Private by default; **share UX = Phase 2**. Streaming via **Lambda Function URL** (no ALB).
- **Agent:** LangGraph multi-graph (`chat`, `ingest`). Chat retrieve = **MultiQuery (~3)**. Dual state: product DB + LangGraph checkpointer.
- **Sources v1:** `LocalUpload` + `GoogleDrive` only. Source abstraction for extension. **No external customer-S3 source** for now. App S3 bucket = storage only.
- **Drive security:** Picker (selected folders/files only); fetch→index→discard temp; never retain non-indexed Drive data; disconnect revokes tokens + purge indexed docs from that source. Google OAuth verification is a real Phase 1 track.
- **Beta economics:** Knowforge pays AI; **rate limits only** (abuse caps). **No billing role, subscriptions, invoices, or BYOK UI** in beta.
- **Quotas (beta):** user + org daily caps — chat 30/200, docs 20/100, embedding tokens 200k/1M (central config).
- **Secrets:** SSM Parameter Store (SecureString) behind `SecretStore`; local `.env` backend for dev.
- **Observability:** Tracer → LangSmith; Bugsnag; `usage_events` in Postgres; CloudWatch logs only (no expensive custom metrics).
- **UI:** English v1; agent follows user’s message language. Breadcrumb = current level + ancestors only.

### Built-in roles (beta)

- **Org:** `owner` | `admin` | `member` (no `billing`)
- **Workspace:** `owner` | `admin` | `member` | `viewer`
- Custom roles = permission bundles; multiple roles per scope; authz = **union (OR)**

### Permission defaults (summary matrix)

Intent for defaults (exact bits live in the future permission catalog / central config):

| Capability | Org owner | Org admin | Org member | WS owner/admin | WS member | WS viewer |
|------------|-----------|-----------|------------|----------------|-----------|-----------|
| Manage org / transfer ownership | ✓ | | | | | |
| Invite to org / create workspaces | ✓ | ✓ | | | | |
| Create private workspace | ✓ | ✓ | | | | |
| Connect sources (e.g. Drive) | | | | ✓ | | |
| Upload / ingest documents | | | | ✓ | ✓ | |
| Chat / use KB | | | | ✓ | ✓ | ✓ |
| Manage workspace members | | | | ✓ | | |
| Public WS access | Implicit for all org members (subject to roles above) | | | | | |

Shared chats (Phase 2): viewers still need workspace KB access (public via org membership, or private via membership).

---

## 6. Baseline codebase (today)

- **Backend:** FastAPI, Mangum/Lambda, SQLAlchemy, Alembic, Postgres + pgvector, S3, **LlamaIndex**-centric RAG (to be retired), OpenAI embeddings/chat.
- **Frontend:** Next.js App Router, React, Tailwind.
- **Infra:** Terraform, API Gateway, ECR, S3 documents bucket.
- **Auth today:** hard-coded `DEV_USER_ID` — replace in M0.2.
- **Upload today:** indexing often **synchronous** in the HTTP request — replace with async JobRunner + ingest graph in Phase 1.
- **Images/multimodal:** already supported — **keep in scope** through Phase 1.

---

## 7. What not to do

- Do not open the full milestone/issue tree on GitHub “for completeness.”
- Do not start Phase 2/3 features (MCP productization, chat share, billing, ALB, external S3 source, reranker as default, etc.) before Phase 1 beta freeze unless the human explicitly changes the plan.
- Do not keep LlamaIndex as long-term orchestrator; do not run two orchestration stacks indefinitely.
- Do not put connector secrets in Secrets Manager one-per-connection; use **SSM** via `SecretStore`.
- Do not mirror a user’s entire Google Drive.
- Do not add customer-facing cost/billing product in beta.

---

## 8. Suggested first prompts in a new session

**Plan-only:**  
> Read `planning/HANDOFF.md`, `planning/ROADMAP.md`, and `planning/MILESTONES.md`. Summarize current status and the next issue to implement. Do not write code yet.

**Implement:**  
> Read `planning/HANDOFF.md`. Implement **`[Cross] Add central config module`** only (slice M0.1.1), following AGENTS.md. Keep the product working; test locally; do not open unrelated milestones.

---

## 9. Doc maintenance

When architecture decisions change: update **`ROADMAP.md`** (and bump a short note here if process changes).  
When backlog order changes: update **`MILESTONES.md`**.  
When the GitHub window or “next work” changes: update **§2** of this file.

---

*This handoff is the bridge between design docs and execution. Prefer editing these files over relying on chat memory.*
