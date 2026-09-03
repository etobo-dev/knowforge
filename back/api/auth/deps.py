from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.auth.identity import AuthenticatedIdentity
from api.auth.jwt import verify_cognito_access_token
from config import Settings, get_settings

_bearer_scheme = HTTPBearer(auto_error=False)


def get_authenticated_identity(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer_scheme),
    ],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthenticatedIdentity:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing bearer token")

    return verify_cognito_access_token(
        settings=settings,
        access_token=credentials.credentials,
    )
