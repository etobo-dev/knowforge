import jwt
from fastapi import HTTPException
from jwt import PyJWKClient

from api.auth.identity import AuthenticatedIdentity
from config import Settings


def _jwks_url(*, settings: Settings) -> str:
    return f"{settings.cognito_issuer_url}/.well-known/jwks.json"


def verify_cognito_access_token(
    *,
    settings: Settings,
    access_token: str,
) -> AuthenticatedIdentity:
    try:
        jwk_client = PyJWKClient(_jwks_url(settings=settings))
        signing_key = jwk_client.get_signing_key_from_jwt(access_token)
        claims = jwt.decode(
            access_token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.cognito_issuer_url,
            options={
                "require": ["exp", "iat", "iss", "sub", "token_use", "client_id"],
            },
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid bearer token") from exc

    token_use = str(claims.get("token_use", "")).strip().lower()
    if token_use != "access":
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    client_id = str(claims.get("client_id", "")).strip()
    if client_id != settings.cognito_app_client_id:
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    cognito_sub = str(claims.get("sub", "")).strip()
    if not cognito_sub:
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    email_raw = claims.get("email")
    email = str(email_raw).strip().lower() if email_raw else None
    if email == "":
        email = None

    return AuthenticatedIdentity(cognito_sub=cognito_sub, email=email)
