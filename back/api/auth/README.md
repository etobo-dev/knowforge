# Testing API authentication

Manual smoke test for Cognito JWT auth on protected routes (`/api/documents`, `/api/chats`).

## Prerequisites

1. Cognito is deployed (`infra/` Terraform apply).
2. API is running locally:

```bash
cd back
uv run uvicorn api.main:app --reload
```

3. `back/.env` has auth enabled and matches your Cognito pool:

```bash
AUTH_DISABLED=false
COGNITO_REGION=us-east-1
COGNITO_USER_POOL_ID=<cognito_user_pool_id>
COGNITO_APP_CLIENT_ID=<cognito_app_client_id>
```

Get these values from the **Infra** GitHub Actions workflow after a successful
`terraform apply` on `main` (`.github/workflows/infra.yml`). Open the latest
deploy run, expand the `terraform apply` step, and copy the outputs at the end of
the log:

- `cognito_user_pool_id`
- `cognito_app_client_id`
- `cognito_region`
- `cognito_hosted_ui_base_url` (for the OAuth URLs below)

If you run Terraform locally, you can also use `terraform output` from `infra/`.

Restart uvicorn after changing `.env`.

## 1. Get an authorization code

Open this URL in the browser (replace `CLIENT_ID`):

```
https://knowforge.auth.us-east-1.amazoncognito.com/oauth2/authorize?response_type=code&client_id=CLIENT_ID&redirect_uri=http://localhost:3000/auth/callback&scope=openid+email+profile&identity_provider=Google
```

Sign in with Google. After redirect, copy the `code` query parameter from the URL
(`http://localhost:3000/auth/callback?code=...`). The front callback page does not
need to be running.

## 2. Exchange the code for tokens

```bash
curl -s -X POST "https://knowforge.auth.us-east-1.amazoncognito.com/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "client_id=CLIENT_ID" \
  -d "code=AUTHORIZATION_CODE" \
  -d "redirect_uri=http://localhost:3000/auth/callback"
```

Use the `access_token` from the JSON response. Do **not** use `id_token`.

## 3. Call a protected endpoint

Without a token (expect `401`):

```bash
curl -i http://localhost:8000/api/documents
```

With a token (expect `200`):

```bash
curl -i http://localhost:8000/api/documents \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

You can also set **Bearer Token** in Postman or Insomnia.

## Notes

- The access token is sent per request in the `Authorization` header. It is not stored in `.env`.
- Tokens expire after 60 minutes (Cognito app client setting).
- For local development without Cognito, set `AUTH_DISABLED=true` in `.env`.
