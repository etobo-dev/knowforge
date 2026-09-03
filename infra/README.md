# Knowforge infrastructure

Terraform for the deployed stack: Cognito (Google IdP), API Lambda + HTTP API, ECR, S3.

## Auth deploy checklist

### 1. Database

From `back/` with production `DATABASE_URL`:

```bash
uv run alembic upgrade head
```

Pre-auth documents/chats under `00000000-0000-0000-0000-000000000001` stay in Postgres/S3; new Google logins get their own `users` row.

### 2. Terraform

Push `infra/` to `main` (`.github/workflows/infra.yml`) or `terraform apply` locally. Lambda env: `COGNITO_USER_POOL_ID`, `COGNITO_APP_CLIENT_ID`, `COGNITO_REGION`. No auth bypass.

```bash
terraform output cognito_app_client_id
terraform output cognito_hosted_ui_base_url
terraform output back_api_endpoint
```

### 3. Front (`knowforge.etobo.tech`)

| Variable | Source |
|----------|--------|
| `NEXT_PUBLIC_API_URL` | `back_api_endpoint` |
| `NEXT_PUBLIC_COGNITO_CLIENT_ID` | `cognito_app_client_id` |
| `NEXT_PUBLIC_COGNITO_HOSTED_UI_BASE_URL` | `cognito_hosted_ui_base_url` |

Callback/logout URLs and CORS already include `https://knowforge.etobo.tech`.

### 4. Smoke

Unauthenticated `GET /api/documents` → `401`. Sign in with Google → upload a PDF → send one chat message.

Local API also requires a Cognito token. See `back/api/auth/README.md`.
