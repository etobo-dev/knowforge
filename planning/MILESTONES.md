# Knowforge — Milestones & Issues (draft)

Short titles + one-line definitions only. Expand later into full GitHub bodies.  
**Order is strict:** finish each issue before the next; finish each milestone before the next.  
Aligned with [`ROADMAP.md`](./ROADMAP.md) rev 3.  
**New session / other agent:** read [`HANDOFF.md`](./HANDOFF.md) first.  
**Diagrams:** [`ARCHITECTURE.md`](./ARCHITECTURE.md).

Production rule: every closed milestone leaves the product **working**; prefer a **noticeable** user-facing change when the dependency chain allows.

### Modules & GitHub issues

Knowforge is organized as **microservices** (like [noticrypt](https://github.com/etobo-tech/noticrypt)). See [`.github/CONTRIBUTING.md`](../.github/CONTRIBUTING.md).

| Mod | Deploy | Responsibility |
|-----|--------|----------------|
| **API** | Lambda REST | HTTP routes, Postgres, authz, quotas, job enqueue |
| **Ingest** | Lambda worker | Sources, extract/index graph, embeddings, vector upsert |
| **Chat** | Lambda SSE + worker | Chat graph, retrieval, streaming, message persistence |
| **Front** | Next.js | UI |
| **Infra** | Terraform | AWS resources |
| **Cross** | — | Shared config, CI, hooks, `planning/`, multi-module changes |

- **GitHub issue title:** `[Mod] Title` — e.g. `[Cross] Add central config module`.
- **GitHub milestone field:** planning milestone name (e.g. `M0.1 — Central configuration`). Not in title or body.
- **Slice ID** (`M0.1.1`): internal row key in this doc only.

### Active window (GitHub)

| Field | Value |
|-------|--------|
| Policy | At most **1** open GitHub milestone and about **≤5–8** issues. Do **not** create the full tree upfront. |
| Current focus | **M0.1 — Central configuration** |
| Next issues | `[Cross] Add central config module` → `[Cross] Point existing code at central config` |
| Not now | Phase 2 / Phase 3 implementation; bulk GitHub milestones |

---

## Phase 0 — Foundations

### M0.1 — Central configuration
Ship shared config so limits/models are not hardcoded.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M0.1.1 | Cross | Add central config module | Create one place for quotas, models, retention, and feature constants. |
| M0.1.2 | Cross | Point existing code at central config | Switch current reads to the new module without changing behavior. |

**Done when:** config changes (e.g. chat daily limit) are edited in one file/env set.

---

### M0.2 — Google login (Cognito)
Users sign in with Google; hard-coded dev user goes away.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M0.2.1 | Infra | Provision Cognito + Google IdP | Create Cognito (local/staging/prod) with Google as IdP. |
| M0.2.2 | API | Verify Cognito JWT on requests | Backend rejects unauthenticated API calls. |
| M0.2.3 | Front | Add Google login and logout | UI can sign in with Google and sign out. |
| M0.2.4 | API | Map Cognito user to app user | Persist `sub`/email; replace `DEV_USER_ID` everywhere. |
| M0.2.5 | Cross | Require auth on production | Deployed app requires login; flows work for signed-in users. |

**Done when:** deployed users must log in with Google to use the app.

---

### M0.3 — Organizations & workspaces
Multi-tenant data model + migrate current docs/chats.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M0.3.1 | API | Add org and workspace schema | Tables for org, workspace (public/private), membership. |
| M0.3.2 | API | Create org on first login | Onboarding creates default public workspace (user = owner). |
| M0.3.3 | API | Scope documents and chats to workspace | Add `organization_id` / `workspace_id`; APIs filter by active workspace. |
| M0.3.4 | API | Backfill existing data to workspace | Move current docs/chats into each user's default public workspace. |
| M0.3.5 | API | Add private workspace and membership | Org owner/admin can create private WS and add/remove members. |

**Done when:** data is per org/workspace; private WS only visible to members.

---

### M0.4 — Navigation (org / workspace)
Noticeable UX: breadcrumb + scoped URLs.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M0.4.1 | Front | Add scoped org and workspace routes | Routes like `/{org}/{ws}/...` for main app areas. |
| M0.4.2 | Front | Add header breadcrumb | Clickable ancestors only (current level + above). |
| M0.4.3 | Front | Add org and workspace switcher | User can switch context; lists only accessible workspaces. |
| M0.4.4 | Front | Centralize English UI strings | User-facing copy in English; strings centralized for later i18n. |

**Done when:** URL/breadcrumb show where you are; switching workspace changes files/chats context.

---

### M0.5 — Roles & permissions
IAM-style permissions without billing.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M0.5.1 | API | Add permission catalog | Fixed list of permission bits (docs, chat, sources, members, …). |
| M0.5.2 | API | Add built-in roles | Org: owner/admin/member; WS: owner/admin/member/viewer. |
| M0.5.3 | API | Add custom roles | Create/edit custom roles as permission bundles (org + workspace). |
| M0.5.4 | API | Attach multiple roles per scope | User can have several roles per scope; authz = union (OR). |
| M0.5.5 | API | Enforce permissions in API | Endpoints check permissions; public WS write defaults applied. |

**Done when:** API denies forbidden actions; custom roles can be assigned.

---

### M0.6 — Invites & settings UI
Teammates can join; admins manage access.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M0.6.1 | API | Add email invite flow | Invite to org and/or workspace with preassigned roles. |
| M0.6.2 | API | Accept invite on login | Invited user lands in the right org/workspace. |
| M0.6.3 | Front | Add org settings page | `/{org}/settings` — members, roles, invites. |
| M0.6.4 | Front | Add workspace settings page | `/{org}/{ws}/settings` — members, roles, invites. |

**Done when:** an owner can invite someone who then sees the shared public (or private) workspace.

---

### M0.7 — Async job backbone
Queues for later ingest/chat workers (no user-facing agent change yet).

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M0.7.1 | Cross | Add JobRunner interface | Abstract enqueue/handle for background jobs. |
| M0.7.2 | Infra | Add SQS and Lambda worker | First transport: SQS triggers Lambda worker. |
| M0.7.3 | Infra | Add EventBridge schedule stub | Hook for scheduled jobs (sync later). |
| M0.7.4 | Cross | Run staging job smoke test | Enqueue a no-op/test job end-to-end in staging. |

**Done when:** a test job runs async in staging via SQS.

---

### M0.8 — Secrets & abuse quotas
Protect keys and cap free beta usage.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M0.8.1 | Cross | Add SecretStore interface | Abstraction for secrets. |
| M0.8.2 | Cross | Add SSM and local env backends | Prod/staging SSM; local `.env` for dev/tests. |
| M0.8.3 | API | Add usage_events ledger | Postgres append-only usage for chat/ingest/embeddings. |
| M0.8.4 | Cross | Add RateLimiter with DynamoDB | Fast daily counters; user + org caps from central config. |
| M0.8.5 | Cross | Enforce quotas on chat and upload | Soft warn then hard block when caps hit. |

**Done when:** hitting chat/upload limits blocks with a clear message; secrets not in plaintext config for staging/prod.

---

### M0.9 — Observability baseline
Errors and agent traces without expensive CloudWatch metrics.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M0.9.1 | Cross | Wire Bugsnag for app errors | Capture exceptions/warnings from API and front. |
| M0.9.2 | Cross | Add Tracer interface | Abstract tracing for later graphs. |
| M0.9.3 | Cross | Wire LangSmith tracer | Beta tracer implementation = LangSmith. |

**Done when:** a forced error appears in Bugsnag; tracer can record a sample span in LangSmith.

---

## Phase 1 — KB agent beta

### M1.1 — Source abstraction + upload path
Extensible ingest entry without Drive yet.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M1.1.1 | Ingest | Add source connector interface | Common contract for list/fetch/credentials/sync hooks. |
| M1.1.2 | Ingest | Add LocalUpload source | Current upload becomes a Source implementation. |
| M1.1.3 | API | Wire upload API through Source | Parent flow uses Source; behavior matches today's upload. |

**Done when:** upload still works in prod via Source abstraction (no LlamaIndex removal yet).

---

### M1.2 — Ingest graph + async indexing
Faster uploads; LangGraph ingest; drop sync-in-request.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M1.2.1 | Ingest | Add extractor plugins | Pluggable extractors (PDF/DOCX/text/image). |
| M1.2.2 | Ingest | Build ingest LangGraph | Nodes: resolve → extract → normalize → chunk → embed → upsert → finalize. |
| M1.2.3 | API | Enqueue ingest on upload | Upload stores file + job; returns without waiting for full index. |
| M1.2.4 | Ingest | Run ingest graph in worker | SQS worker executes ingest; status progresses to indexed/failed. |
| M1.2.5 | Ingest | Remove sync-in-request indexing | Remove old blocking index path after cutover. |

**Done when:** user uploads and UI shows processing→indexed asynchronously; old sync path gone.

---

### M1.3 — Streaming chat shell (Function URL)
Noticeable: tokens stream while agent still legacy underneath (or thin stub).

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M1.3.1 | Chat | Add ChatRunEvent contract | Versioned SSE events: node/token/sources/done/error. |
| M1.3.2 | Chat | Add Lambda Function URL for SSE | Streaming endpoint (no ALB); auth still Cognito. |
| M1.3.3 | Front | Consume SSE in chat UI | Chat UI streams tokens instead of waiting for full reply. |
| M1.3.4 | Chat | Bridge legacy chat to SSE | Temporarily stream legacy LlamaIndex replies over the new pipe. |

**Done when:** chat answers appear token-by-token in production via Function URL.

---

### M1.4 — LangGraph chat + MultiQuery
Real agent cutover for chat.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M1.4.1 | Chat | Add chat graph skeleton | Nodes load→understand→plan→retrieve→grade→tools→generate→persist. |
| M1.4.2 | Chat | Add MultiQuery retrieve | Reformulate query thrice, retrieve, fuse/dedupe. |
| M1.4.3 | Chat | Add multimodal branch | Keep image-aware generate when image nodes hit. |
| M1.4.4 | Chat | Persist dual state | Product DB messages/sources + LangGraph checkpointer. |
| M1.4.5 | Chat | Cut over chat to LangGraph | SSE runs LangGraph; legacy chat engine removed. |

**Done when:** production chat is LangGraph + MultiQuery; LlamaIndex chat engine gone.

---

### M1.5 — Citations panel
Noticeable trust UX.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M1.5.1 | Chat | Persist structured sources | Store citation payloads from the graph. |
| M1.5.2 | Front | Add inline citations and sources panel | UI shows markers and a panel with excerpts/links. |

**Done when:** each answer shows sources the user can open.

---

### M1.6 — Retriever behind interface (+ hybrid if capacity)
Clean retrieval; optional hybrid before beta freeze.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M1.6.1 | Chat | Add retriever interface | Support vector / hybrid / hybrid+rerank. |
| M1.6.2 | Chat | Cut over vector retriever | Text + image vector search via new stack (not LlamaIndex). |
| M1.6.3 | Chat | Add hybrid retriever (optional) | Vector + Postgres FTS fused (RRF); ship if milestone time allows. |

**Done when:** retrieval no longer depends on LlamaIndex; hybrid optional.

---

### M1.7 — Google Drive source
Second real source; picker + safe retention.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M1.7.1 | Infra | Create GCP OAuth app for Drive | Knowforge OAuth client; verification track started. |
| M1.7.2 | Ingest | Connect Drive and Picker | User selects folders/files only; tokens in SecretStore. |
| M1.7.3 | Ingest | Enqueue Drive fetch as ingest job | Selected files enqueue ingest; no mirror of whole Drive. |
| M1.7.4 | Ingest | Disconnect Drive and purge | Revoke tokens; soft-delete indexed docs from that source. |
| M1.7.5 | Ingest | Add manual Drive sync button | User can "Sync now" for a Drive source. |

**Done when:** user connects Drive, picks folders, files appear indexed; disconnect cleans up.

---

### M1.8 — Scheduled sync
Keep Drive (and future sources) fresh.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M1.8.1 | Ingest | Add SyncStrategy interface | manual \| scheduled \| webhook. |
| M1.8.2 | Ingest | Add scheduled sync via EventBridge | Periodic sync for connected sources. |

**Done when:** Drive sources refresh on a schedule without manual click.

---

### M1.9 — Soft delete, purge, export
Data lifecycle basics.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M1.9.1 | API | Add soft delete for docs, chats, sources | Deleted items hidden; retained per config (30d). |
| M1.9.2 | Cross | Add hard purge job | After retention, delete S3, chunks, vectors, checkpointer bits. |
| M1.9.3 | API | Add org data export | Owner can export org data package. |

**Done when:** delete is reversible for 30 days then purged; export works for owner.

---

### M1.10 — Retire LlamaIndex
Dependency cleanup after all cutovers.

| ID | Mod | Title | Definition |
|----|-----|-------|------------|
| M1.10.1 | Cross | Remove LlamaIndex usage | No imports/deps left; LangGraph/LangChain + pgvector only. |
| M1.10.2 | Cross | Run staging full checklist | Auth, upload, Drive, SSE chat, citations, quotas, delete—all green. |

**Done when:** LlamaIndex removed; staging checklist signed off → **external beta**.

---

## Phase 2 — Extension (outline only)

| Milestone | Short definition |
|-----------|------------------|
| M2.1 MCP tools | Connect MCP servers; `call_tools` in chat graph. |
| M2.2 Chat sharing | Explicit share of a private chat inside a workspace. |
| M2.3 Citation preview | PDF/page or image preview from a citation. |
| M2.4 Webhook sync | SyncStrategy webhook implementations. |
| M2.5 Fargate workers | Optional long-running JobRunner transport. |
| M2.6 Reranker | hybrid+rerank retriever. |
| M2.7 UI i18n EN/ES | Second locale for UI. |
| M2.8 Run inspector | Optional admin/user view of run traces. |

*(Expand issues when Phase 1 is done.)*

---

## Phase 3 — Platform (outline only)

| Milestone | Short definition |
|-----------|------------------|
| M3.1 More connectors | New Sources as needed (e.g. external S3 if revisited). |
| M3.2 Evals & analytics | Quality evals; org usage dashboards. |
| M3.3 Enterprise auth options | Domain auto-join, etc. |

---

## Suggested build order (checklist)

```
M0.1 → M0.2 → M0.3 → M0.4 → M0.5 → M0.6 → M0.7 → M0.8 → M0.9
  → M1.1 → M1.2 → M1.3 → M1.4 → M1.5 → M1.6 → M1.7 → M1.8 → M1.9 → M1.10
  → Phase 2 …
```

Noticeable production moments (examples):

- End **M0.2** — Google login  
- End **M0.4** — org/workspace navigation  
- End **M0.6** — invites / team access  
- End **M1.2** — async indexing  
- End **M1.3** — streaming chat  
- End **M1.5** — citations  
- End **M1.7** — Google Drive  
- End **M1.10** — beta freeze  

---

*Next: create GitHub milestone + issues for the active window → start `[Cross] Add central config module`.*
