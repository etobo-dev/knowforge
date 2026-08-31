# Knowforge Product Roadmap

Status: **design documented; self-reviewed (rev 3)**.  
**Start here for a new session:** [`HANDOFF.md`](./HANDOFF.md) (reading order, GitHub window, next work = M0.1).  
**Architecture diagrams:** [`ARCHITECTURE.md`](./ARCHITECTURE.md).  
**Commits & issues:** [`.github/CONTRIBUTING.md`](../.github/CONTRIBUTING.md).  
Backlog titles: [`MILESTONES.md`](./MILESTONES.md).

> **Rev 3** closes open items from rev 2: simpler quotas (abuse caps only), SSE = **Lambda Function URL** (no ALB), **no billing/cost product in beta**. See [§9](#9-self-review-findings-rev-2).

## 1. Product vision

Knowforge is a **multi-tenant SaaS knowledge-base agent**:

- Organizations contain **workspaces** (default public workspace + optional private workspaces).
- Users sign in with **Google via Amazon Cognito**.
- Knowledge is ingested from **extensible sources** (v1: local upload + Google Drive).
- Users query the active workspace KB through a **chat agent** orchestrated by **LangGraph** (multi-graph platform).
- The product must remain **continuously functional** while evolving; legacy paths are removed only after a full cutover.

## 2. Non-negotiable delivery principles

| Principle | Rule |
|-----------|------|
| Always working | Every merged change leaves a usable product. |
| Atomic milestones | Each milestone is completable on its own. |
| Atomic issues | Ordered so one issue can be finished without parallel work on another. |
| Local first | Build and test locally; connect to the **parent/production flow** when possible; push only if nothing breaks. |
| Cutover then delete | When a feature fully replaces legacy, disconnect and **delete** old logic—no long dual stacks in prod. |
| Abstractions | Prefer interfaces so features stay extensible (sources, jobs, LLM, secrets, retriever, tracer, rate limiter). |
| Central config | Quotas, model names, retention days, and similar constants live in **centralized config files**, not scattered in business logic. |
| Cost-aware | Prefer cheap secret/ops choices (SSM, avoid expensive CloudWatch custom metrics, no per-connection Secrets Manager). |

Quality bar before retiring legacy (**D**):

1. Unit tests  
2. Integration tests (keep backend coverage culture, currently ≥90%)  
3. LangGraph node / golden-path tests where applicable  
4. Staging checklist (auth, upload/sync, SSE chat, etc.)  
5. Only then cutover + delete old code  

## 3. Current baseline (today)

Already in the repo (to be evolved, not abandoned overnight):

- FastAPI + Lambda/Mangum, Next.js front, Postgres + pgvector, S3 (app storage), LlamaIndex-centric RAG chat/upload.
- Single hard-coded dev user; sync indexing inside the HTTP upload request.
- **Target:** LangGraph + LangChain orchestration; **retire LlamaIndex** as a dependency (extractors `pypdf` / `python-docx` stay).

## 4. Architecture decisions (locked)

### 4.1 Tenancy and access

- **SaaS multi-tenant** with full **Organization + Workspace** from day one (no half-measure schema).
- **ACL granularity = workspace**, not per file.
- Each org has a **default public workspace**.
  - **Access rule:** any **org member** may access the public workspace **implicitly** (no per-user workspace membership row required for the public WS).
  - They can navigate its files and chat against its KB **subject to org/workspace role permissions**.
- **Private workspaces:** created by **org owner or org admin**; only users with **explicit workspace membership** may access files or chat there.
- **Chat retrieval is single-workspace**: one chat ↔ one `workspace_id` (breadcrumb context). No automatic cross-workspace retrieval.
- Public workspace write policy: **role-based** (defaults: members upload + chat; admins manage sources / destructive ops / private WS membership). Custom roles can override.
- **Existing data migration (required):** today’s `documents.user_id` / `chats.user_id` model must move to `organization_id` + `workspace_id` (backfill into each user’s default public workspace when AuthN lands). This was missing from rev 1.

### 4.2 Auth and authorization

- **Cognito** = AuthN only (Google-first). JWT proves identity.
- **AuthZ** = Knowforge DB (orgs, workspaces, role attachments, permission catalog).
- Do **not** put product roles in Cognito Groups.
- Onboarding: first login creates **Org + default public Workspace** (user as owner). **Email invites** carry preassigned org and/or workspace roles.
- Dual RBAC: roles at **Org and Workspace**; **multiple roles per user per scope** (permission union / OR).
- Built-in roles as system presets; **IAM-style custom roles** at both scopes (permission bundles from a fixed permission catalog). No Deny policies in v1.
- **Built-in role names (beta):**
  - **Org:** `owner` | `admin` | `member`
  - **Workspace:** `owner` | `admin` | `member` | `viewer`
  - Exact permission bits live in the permission catalog (central config / code constants); custom roles compose the same bits.
  - **No `billing` role and no cost/subscription/BYOK product surfaces in beta.** Knowforge assumes AI cost; abuse control is **rate limits only**. Billing/subscription/BYOK stay as future extension points only.

### 4.3 Chat product model

- Chats are **private per user** within a workspace by default.
- **Explicit share** is in the product model; **share UX ships in Phase 2** (beta can ship without sharing). Shared viewers still need access to that workspace’s KB (public WS via org membership, or private WS membership).
- Product DB (`chats` / `messages` / `message_sources`) = **source of truth** for UI, sharing, RBAC, citations. (Not to be confused with Source **connectors**.)
- LangGraph **Postgres checkpointer** = execution state (retries, tool loops, interrupts); sync to product DB at end of turn.
- Delivery: **async job + SSE** `ChatRunEvent` stream (`node_started`, `token`, `sources`, `done` / `error`). WebSocket later if needed for presence.
- **SSE transport (locked for beta):** **Lambda Function URL** (not ALB). Same `ChatRunEvent` contract; validate streaming in staging. API Gateway remains fine for non-streaming REST.
- Citations: **inline `[n]` + sources panel** in Phase 1 chat cutover; rich PDF/image preview in Phase 2.
- **Images / multimodal:** already in the current product (PNG/JPEG ingest + fused image retrieval). **Remain in scope** for Phase 1 unless explicitly cut later; ingest/chat graphs must keep an image path (vision describe → embed; multimodal generate when image nodes are retrieved).

### 4.4 Agent platform (LangGraph)

- **Multi-graph registry** (`AgentGraph`): versioned graphs.
- V1 graphs: **`chat`** and **`ingest`**.
- End-state: **no LlamaIndex**; LangGraph + LangChain for LLM, embeddings, splitters, vector integration, memory patterns.

**Chat graph nodes (v1):**

1. `load_session`  
2. `understand`  
3. `plan_retrieval`  
4. `retrieve` — **MultiQuery (~3 reformulations → retrieve → fuse/dedupe)**  
5. `grade_documents`  
6. `call_tools` (conditional; MCP later)  
7. `generate`  
8. `persist`  

**Ingest graph nodes (v1):**

1. `resolve_source_object`  
2. `extract` (pluggable `Extractor` by MIME)  
3. `normalize`  
4. `chunk`  
5. `embed`  
6. `upsert_store`  
7. `finalize`  

### 4.5 Retrieval

- `Retriever` interface: `vector` | `hybrid` | `hybrid+rerank`.
- First cutover: **vector + MultiQuery**.
- **Hybrid** (vector + Postgres FTS/BM25, e.g. RRF) before external beta if the milestone allows.
- **Reranker** in Phase 2.

### 4.6 Sources and sync

- Abstract **`Source` connector** from day one (easy to extend).
- **V1 implementations:** `LocalUpload`, `GoogleDrive` only.  
  - **No external customer-S3 source** for now. Knowforge’s own S3 bucket remains **app storage** only.
- MCP modeled as `MCPConnection` with modes `tools` | `index` | `both`; ship **tools-in-chat first**, index later.
- **`SyncStrategy`:** `manual` | `scheduled` | `webhook`. V1: manual + scheduled; webhooks later.
- Canonical event `SourceObjectChanged` → **async** ingest (not sync-in-HTTP).
- **Google Drive:** Knowforge-owned GCP OAuth app for **production beta with real users** (consent screen OK; **not** “Testing mode only” as the long-term plan).  
  - **Phase 1 blocker:** Google **OAuth app verification** (sensitive Drive scopes) must be planned as a real work item—without it, Drive cannot be offered broadly to arbitrary Google accounts in production.  
  **Security (mandatory):** user **picks folders/files** (Picker); **zero retention** of non-indexed Drive data (`fetch → index → discard temp`); Disconnect revokes tokens + soft-delete/purge indexed docs from that source; audit fetched file IDs; clear privacy/ToS.

### 4.7 Jobs and runtime

- **`JobRunner` abstraction**; v1 transport: **SQS + Lambda workers** + EventBridge schedules.
- Same contract migratable to **Fargate** for long LangGraph/MCP runs (Lambda 15 min limit).

### 4.8 LLM, quotas, secrets, observability

- **`LLMProvider` / `EmbeddingProvider` abstraction.** Beta: Knowforge-managed OpenAI; **Knowforge pays**; **low rate limits** to prevent abuse. **No billing, subscriptions, invoices, or BYOK in the beta product.** Those remain future-ready behind the provider/quota abstractions only.
- **Quotas (abuse caps, not pricing):**  
  In plain terms: each day we count how much AI/ingest a **user** and an **org** used. If they hit the cap → soft warning, then hard block until the next day. This is only to stop runaway spend while Knowforge pays the OpenAI bill—not to charge customers.

  **Beta enforces only user + org** (simple). Workspace-level and tool-call counters may exist later in the `RateLimiter` design; **not required for beta UI or defaults**.

  | What we count | Max per user / day | Max per org / day |
  |---------------|--------------------|-------------------|
  | Chat turns (messages that run the agent) | 30 | 200 |
  | Documents ingested | 20 | 100 |
  | Embedding tokens | 200k | 1M |

  All numbers live in **central config** (easy to change).

- **`RateLimiter`:** DynamoDB fast path (v1); Postgres **`usage_events`** (+ daily aggregates) = business ledger.
- **Secrets:** all via **SSM Parameter Store SecureString** behind `SecretStore` (paths per env/org). No Secrets Manager in base design.
  - **Local/dev:** `SecretStore` may use `.env` / local file backend implementing the same interface (do not require real SSM for unit tests or solo local runs).
- Observability: **`Tracer` → LangSmith** (beta); **Bugsnag** for bugs/warnings; **Postgres usage** for business; CloudWatch = **minimal logs only** (no expensive custom metrics).

### 4.9 Data lifecycle

- Soft delete + hard purge after **30 days** (central config).
- Org owner **data export**; account/org delete **cascades**.
- Purge covers S3 objects, chunks, vectors, messages, and related checkpointer threads.
- Per-org retention settings later.

### 4.10 Frontend / i18n / environments

- Scoped routes + **clickable breadcrumb** in header: show **current level and ancestors only**.
- User segment in URL only when relevant (e.g. chats); files/sources under `/{org}/{ws}/...` without fake per-user ownership.
- Settings: `/{org}/settings` and `/{org}/{ws}/settings` (members, invites, roles).
- UI **English** in v1 (centralize strings for later locales); agent answers in the **user’s message language**. Full EN/ES UI in Phase 2.
- Environments: **local + staging + prod** (SSM/config paths per env).

### 4.11 Migration strategy

**Strangler D:** foundations → new ingest/chat beside old → cutover → **delete** LlamaIndex/legacy.  
Never big-bang. Feature-complete replacement then wire + remove old.

## 5. Phased roadmap

External **beta** ≈ end of **Phase 1**.

### Phase 0 — Foundations (product stays usable)

Goal: identity, tenancy, authz, jobs, config, quotas, observability scaffolding—without breaking current upload/chat.

Suggested milestone themes (atomic issues later):

1. Central config module (quotas, models, retention, feature constants).  
2. Cognito AuthN + replace `DEV_USER_ID` with real user mapping (compatible cutover: existing data keeps working).  
3. Org + Workspace schema; default **public** workspace; private workspace membership; **backfill** existing documents/chats into default public WS.  
4. Permission catalog + built-in roles (`owner`/`admin`/`member` + WS roles; **no billing role**) + custom roles + multi-role attach.  
5. Invites + scoped settings UI (members/roles).  
6. Front: org/ws switcher, breadcrumb routes, English UI strings.  
7. `JobRunner` + SQS (+ EventBridge stub); staging env wiring.  
8. `SecretStore` (SSM + local `.env` backend); `RateLimiter` (Dynamo) + `usage_events`.  
9. Bugsnag + Tracer interface (LangSmith wired).  

### Phase 1 — KB agent beta

Goal: extensible ingest + LangGraph chat; Upload + Drive; async; SSE; cutover off LlamaIndex; keep image/multimodal path.

1. `Source` abstraction + `LocalUpload` behind new ingest path (parent-flow tested).  
2. `ingest` LangGraph + Extractor plugins (text + image); async indexing cutover; delete sync-in-request path.  
3. Google Drive source (Picker, tokens in SSM, zero non-indexed retention, disconnect/purge) **including OAuth verification track**.  
4. `SyncStrategy` manual + scheduled.  
5. `chat` LangGraph + MultiQuery retrieve + multimodal branch; dual state (DB + checkpointer).  
6. SSE via **Lambda Function URL**; front streaming + inline citations panel.  
7. Vector retriever cutover (text + image stores); hybrid retriever if milestone capacity allows.  
8. Soft-delete / purge / export basics.  
9. Retire LlamaIndex dependency; keep product green on staging checklist.  
10. *(Explicit non-goal for Phase 1)* Chat **share** UX → Phase 2 (model may reserve fields earlier if needed).

### Phase 2 — Extension

- MCP connections (`tools`, then `index`).  
- Chat sharing UX.  
- Citation rich preview.  
- Webhook sync strategies.  
- Fargate worker path if needed.  
- BYOK / subscription / billing product (post-beta; not in beta).  
- Reranker.  
- UI i18n EN/ES.  
- Optional run inspector.  

### Phase 3 — Platform

- More source connectors (e.g. external S3 with prefix allowlist—only if revisited).  
- Evals / datasets, admin analytics, domain auto-join, enterprise OAuth options, etc.  

## 6. Explicit non-goals (near term / beta)

- External **customer S3** as a Source.  
- Per-file ACL.  
- Cross-workspace chat retrieval by default.  
- LangChain/LangGraph dual-running with LlamaIndex long-term.  
- Cognito as AuthZ source of truth.  
- Secrets Manager per connection.  
- Expensive CloudWatch custom metrics as primary telemetry.  
- **Any customer-facing cost management** in beta (billing role, subscriptions, invoices, BYOK UI, usage-based charging).  
- **ALB** for chat streaming (use Function URL).  
- Enforcing separate **workspace/day** or **tool_calls** quota defaults in beta (user + org caps only).

## 7. Execution process (see HANDOFF)

- Full backlog lives in [`MILESTONES.md`](./MILESTONES.md) as a **north star** (not all tickets opened at once).
- GitHub: **rolling window** — ≤1 open milestone, few issues; expand when starting work ([`HANDOFF.md`](./HANDOFF.md) §3).
- Next implementation slice: **M0.1** (central configuration).

## 8. Decision log (grill-me)

| # | Topic | Choice |
|---|--------|--------|
| 1 | Product shape | SaaS multi-tenant |
| 2 | Tenant model | Org + Workspace from day one |
| 3–5 | RBAC | Dual org/ws; multi-role OR; custom IAM roles |
| 6–7 | Auth | Cognito AuthN; AuthZ in app DB |
| 8 | Onboarding | Auto org+public WS + role invites |
| 9 | Chats | Private default + optional share |
| 10–11 | Sources/sync | Source abstraction; Upload+Drive; SyncStrategy hybrid; async ingest |
| 12 | Jobs | JobRunner; SQS+Lambda → Fargate-ready |
| 13–16 | Agents | Multi-graph; chat+ingest; MultiQuery; dual state |
| 17 | Chat delivery | Async + SSE |
| 18–19 | LLM/quotas | Provider abstraction; managed keys + low limits; Dynamo RateLimiter + usage DB |
| 20 | MCP | Dual mode tools+index (tools first) |
| 21 | Secrets | SSM for all |
| 22 | Observability | LangSmith Tracer + Bugsnag + usage DB |
| 23–24 | Delivery | Phases 0–3; strangler cutover-delete; atomic milestones/issues |
| 25 | Envs | Local + staging + prod |
| 26 | Retrieval | Vector+MultiQuery → hybrid → rerank |
| 27 | Citations | Inline+panel; preview later |
| 28 | Data lifecycle | Soft delete 30d + export + cascade |
| 29–30 | Front | Breadcrumb scoped URLs; scoped settings |
| 31 | RateLimiter store | Abstraction + DynamoDB v1 |
| 32 | i18n | EN UI v1; agent follows user language |
| 33 | Quality | Bar D + parent-flow test before push |
| 34 | Drive | Knowforge OAuth + picker + zero non-indexed retention |
| 35 | S3 source | Deferred; keep Source extensible |
| 36–37 | ACL/chat scope | Workspace ACL; public default WS; chat = one WS |

## 9. Self-review findings (rev 2)

Issues found in rev 1 and how they were handled:

| Severity | Finding | Fix |
|----------|---------|-----|
| High | Public vs private workspace **access rule** was ambiguous (implicit org access vs membership rows). | Clarified: public WS = implicit for org members; private = explicit membership; create = org owner/admin. |
| High | No plan to **migrate** existing `user_id` documents/chats into org/workspace. | Added backfill requirement in §4.1 and Phase 0. |
| High | **SSE over API Gateway + Lambda** stated as if trivial; streaming often fails timeouts. | Added infra note + Phase 1 “validate transport in staging”. |
| High | **Google OAuth verification** understated for a real-user unpaid beta. | Marked as Phase 1 blocker / work track for Drive. |
| Medium | **Chat share** listed as core capability but omitted from Phase 1 → contradiction. | Share UX = Phase 2; beta can ship without share. |
| Medium | Quota table was confusing (workspace/tool_calls). | **Rev 3:** beta = simple user+org caps only; explained as abuse limits, not pricing. |
| Medium | **Built-in role names** / billing. | **Rev 3:** no `billing` role; beta has zero cost-management product. |
| High | SSE transport. | **Rev 3:** **Lambda Function URL**; no ALB for now. |

Still **open / needs your call** (not silently invented beyond starting defaults):

~~resolved in rev 3 — see below~~

### Rev 3 resolutions (your answers)

1. **Quotas:** Explained in plain language; beta table back to **user + org only** (30/200 chat, 20/100 docs, 200k/1M embed). No workspace/tool_calls defaults in beta.
2. **SSE:** **Lambda Function URL**; **no ALB** for now.
3. **Billing:** **None in beta**—no billing role, no subscriptions, no cost UI. Knowforge pays; rate limits only.

---

*Rev 3 — open items from self-review closed. Implementation starts only after milestone/issue breakdown is requested.*
