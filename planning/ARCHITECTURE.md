# Knowforge — Target Architecture (beta)

Visual reference for how the system works **after Phase 1** (external beta).  
Aligned with [`ROADMAP.md`](./ROADMAP.md) rev 3 and [`HANDOFF.md`](./HANDOFF.md).

**Today:** parts of this are still LlamaIndex + sync upload; see [§6 Current vs target](#6-current-vs-target).

---

## 1. System overview

```mermaid
flowchart TB
    subgraph Users
        U[User browser]
    end

    subgraph Frontend["Next.js (knowforge.etobo.tech)"]
        UI[App UI<br/>breadcrumb org/ws]
        SSE[SSE client<br/>ChatRunEvent]
    end

    subgraph AuthN["AuthN"]
        CG[Google OAuth]
        COG[Amazon Cognito]
    end

    subgraph Edge["AWS edge"]
        APIGW[API Gateway HTTP<br/>REST /api/*]
        FURL[Lambda Function URL<br/>SSE chat stream]
    end

    subgraph API["FastAPI on Lambda"]
        REST[REST handlers<br/>documents, chats, sources, settings]
        AUTHZ[AuthZ middleware<br/>org/ws roles + permissions]
        QUOTA[RateLimiter check]
    end

    subgraph Jobs["Async jobs"]
        SQS[SQS queues]
        WRK[Lambda workers<br/>JobRunner]
        EB[EventBridge<br/>scheduled sync]
    end

    subgraph Agents["LangGraph (multi-graph)"]
        ING[ingest graph]
        CHAT[chat graph<br/>MultiQuery retrieve]
        CKPT[Postgres checkpointer]
    end

    subgraph Data["Data plane"]
        PG[(PostgreSQL<br/>product + RBAC + usage_events)]
        PGV[(pgvector<br/>text + image indexes)]
        S3[(S3 bucket<br/>file blobs)]
        DDB[(DynamoDB<br/>daily quota counters)]
    end

    subgraph Sources["Knowledge sources"]
        UP[LocalUpload]
        GD[Google Drive<br/>Picker + OAuth]
    end

    subgraph External["External services"]
        OAI[OpenAI<br/>embed / chat / vision]
        GCP[Google Drive API]
        SSM[SSM Parameter Store<br/>secrets]
        LS[LangSmith]
        BN[Bugsnag]
    end

  U --> UI
  U --> CG --> COG
  UI -->|JWT| APIGW
  UI -->|JWT| FURL
  SSE <-->|events| FURL

  APIGW --> REST
  FURL --> CHAT
  REST --> AUTHZ --> QUOTA
  REST -->|enqueue| SQS
  EB -->|schedule| SQS
  SQS --> WRK
  WRK --> ING
  WRK --> CHAT

  REST --> PG
  ING --> PG
  ING --> PGV
  ING --> S3
  CHAT --> PG
  CHAT --> PGV
  CHAT --> CKPT
  CKPT --> PG

  UP --> ING
  GD -->|fetch selected files| ING
  GD -.-> GCP
  ING --> OAI
  CHAT --> OAI

  REST -.-> SSM
  WRK -.-> SSM
  REST --> DDB
  REST --> BN
  CHAT --> LS
  ING --> LS
```

**Read left → right:** user → front → edge → API/jobs → agents → data → external.

---

## 2. Tenancy & request context

Every authenticated request carries **org + workspace** context (from route/breadcrumb). AuthZ runs in the app DB, not Cognito.

```mermaid
flowchart LR
    JWT[Cognito JWT<br/>identity only] --> MAP[Map to app user]
    MAP --> CTX[Request context<br/>org_id + workspace_id]
    CTX --> RBAC[Resolve roles<br/>org + workspace<br/>union OR]
    RBAC --> PERM{Permission?}
    PERM -->|allow| H[Handler]
    PERM -->|deny| E[403]

    subgraph Workspaces
        PUB[Public WS<br/>all org members]
        PRIV[Private WS<br/>explicit members only]
    end

    CTX --> PUB
    CTX --> PRIV
```

- **Public workspace:** implicit access for all org members (read/chat/upload per role).
- **Private workspace:** only listed members; org owner/admin creates it.
- **Chat:** scoped to **one** workspace; retrieval never crosses workspaces.

---

## 3. Ingest flow (upload or Drive sync)

Indexing is **async** (not blocking the HTTP response).

```mermaid
sequenceDiagram
    participant UI as Frontend
    participant API as REST API
    participant Q as SQS
    participant W as Worker Lambda
    participant S as Source connector
    participant G as ingest LangGraph
    participant S3 as S3
    participant PG as PostgreSQL
    participant V as pgvector
    participant OAI as OpenAI

    UI->>API: POST upload / trigger sync
    API->>API: AuthZ + quota check
    API->>S3: Store blob (upload path)
    API->>PG: Document status=uploading
    API->>Q: Enqueue ingest job
    API-->>UI: 202 / document row

    Q->>W: Job message
    W->>S: resolve_source_object
    alt LocalUpload
        S->>S3: Read bytes
    else Google Drive
        S->>S: Fetch selected file only
        Note over S: fetch → index → discard temp<br/>no full Drive mirror
    end

    W->>G: Run ingest graph
    G->>G: extract → normalize → chunk
    G->>OAI: embed batch
    G->>PG: document_chunks
    G->>V: upsert vectors (workspace scoped)
    G->>PG: status=indexed / failed
```

**Ingest graph nodes:** `resolve_source_object` → `extract` → `normalize` → `chunk` → `embed` → `upsert_store` → `finalize`.

---

## 4. Chat flow (streaming)

Chat runs as an **async job**; tokens stream over **SSE** via **Lambda Function URL** (not API Gateway, not ALB).

```mermaid
sequenceDiagram
    participant UI as Frontend
    participant FURL as Lambda Function URL
    participant API as Chat orchestration
    participant Q as SQS
    participant W as Worker Lambda
    participant C as chat LangGraph
    participant V as pgvector
    participant PG as PostgreSQL
    participant CK as Checkpointer
    participant OAI as OpenAI

    UI->>FURL: POST message (JWT)
    FURL->>API: AuthZ + quota
    API->>Q: Enqueue chat run
    API-->>UI: run_id

    UI->>FURL: GET SSE /runs/{id}
    Q->>W: Start chat job
    W->>C: load_session (workspace KB only)
    C->>C: understand → plan_retrieval
  loop MultiQuery (~3)
        C->>OAI: Reformulate query
        C->>V: Vector search (user+ws filter)
    end
    C->>C: fuse/dedupe → grade_documents
    opt Image nodes retrieved
        C->>OAI: Multimodal generate
    else Text only
        C->>OAI: Generate with citations
    end
    C->>CK: Execution state
    C->>PG: messages + message_sources
    W-->>UI: SSE tokens, sources, done
```

**Chat graph nodes:** `load_session` → `understand` → `plan_retrieval` → `retrieve` (MultiQuery) → `grade_documents` → `call_tools` (optional, MCP later) → `generate` → `persist`.

**Dual state:** product DB = UI/history/citations; LangGraph checkpointer = retries/tool loops.

---

## 5. Data model (core entities)

Simplified ER for beta. ACL is **workspace-level**, not per document.

```mermaid
erDiagram
    ORGANIZATIONS ||--o{ WORKSPACES : has
    ORGANIZATIONS ||--o{ ORG_MEMBERSHIPS : has
    USERS ||--o{ ORG_MEMBERSHIPS : member_of
    WORKSPACES ||--o{ WS_MEMBERSHIPS : has
    USERS ||--o{ WS_MEMBERSHIPS : member_of

    WORKSPACES ||--o{ DOCUMENTS : contains
    DOCUMENTS ||--o{ DOCUMENT_CHUNKS : has
    WORKSPACES ||--o{ SOURCES : connects
    WORKSPACES ||--o{ CHATS : contains
    CHATS ||--o{ MESSAGES : has
    MESSAGES ||--o{ MESSAGE_SOURCES : cites
    MESSAGE_SOURCES }o--|| DOCUMENT_CHUNKS : references

    ORGANIZATIONS ||--o{ ROLES : defines
    ROLES ||--o{ ROLE_PERMISSIONS : grants
    USERS ||--o{ ROLE_ATTACHMENTS : has

    USERS ||--o{ USAGE_EVENTS : generates
```

**Vector storage:** `document_chunks` metadata + pgvector tables (`knowforge_vectors`, `knowforge_vectors_image`) filtered by `workspace_id` at query time.

---

## 6. Current vs target

| Area | Today (repo) | Target (beta) |
|------|----------------|---------------|
| Auth | `DEV_USER_ID` hard-coded | Cognito + Google |
| Tenancy | per `user_id` | org + workspace |
| Upload/index | sync in HTTP request | SQS + ingest graph |
| Chat | LlamaIndex `ContextChatEngine` | LangGraph chat graph + SSE |
| Streaming | full response wait | Function URL SSE |
| Sources | upload only | Upload + Google Drive |
| Secrets | env vars | SSM + `SecretStore` |
| Quotas | none | DynamoDB + `usage_events` |

Migration: **strangler** — build beside legacy, cut over, delete old path (see ROADMAP §4.11).

---

## 7. Phase 2+ (outline on diagram only)

Not in beta scope; shown for direction:

```mermaid
flowchart LR
    subgraph Phase2["Phase 2 (later)"]
        MCP[MCP tools + index]
        SHARE[Chat sharing UX]
        HYB[Hybrid + rerank retriever]
    end

    CHAT[chat graph] -.-> MCP
    CHAT -.-> SHARE
    RET[Retriever] -.-> HYB
```

---

## 8. Related docs

| Doc | Content |
|-----|---------|
| [`HANDOFF.md`](./HANDOFF.md) | How to continue work; active window |
| [`ROADMAP.md`](./ROADMAP.md) | Locked decisions and phases |
| [`MILESTONES.md`](./MILESTONES.md) | Ordered delivery backlog |
| [`.github/CONTRIBUTING.md`](../.github/CONTRIBUTING.md) | Commits & issues format |

---

*Target architecture for planning. Update when major decisions change.*
