import jwt
from fastapi import HTTPException
from jwt import PyJWKClient
from jwt.types import Options

from api.auth.identity import AuthenticatedIdentity
from config import Settings

_COGNITO_ACCESS_TOKEN_DECODE_OPTIONS: Options = {
    "require": [
        "exp",
        "iat",
        "iss",
        "sub",
        "token_use",
        "client_id",
    ],
}


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
            options=_COGNITO_ACCESS_TOKEN_DECODE_OPTIONS,
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid bearer token") from exc

    token_use = str(claims.get("token_use", "")).strip().lower()
    client_id = str(claims.get("client_id", "")).strip()
    cognito_sub = str(claims.get("sub", "")).strip()
    if any(
        (
            token_use != "access",
            client_id != settings.cognito_app_client_id,
            not cognito_sub,
        )
    ):
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    email_raw = claims.get("email")
    email = None if email_raw is None else str(email_raw).strip().lower() or None

    return AuthenticatedIdentity(cognito_sub=cognito_sub, email=email)
