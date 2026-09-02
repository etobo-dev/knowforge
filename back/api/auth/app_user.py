from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from api.auth.deps import AUTH_DISABLED_SUB, get_authenticated_identity
from api.auth.identity import AuthenticatedIdentity
from config import Settings, get_settings
from db.models import User
from db.repositories.users import (
    db_get_or_create_user_by_cognito_sub,
    db_get_or_create_user_with_id,
)
from db.session import get_db

AUTH_DISABLED_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


def get_current_app_user(
    identity: Annotated[AuthenticatedIdentity, Depends(get_authenticated_identity)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    if settings.auth_disabled:
        return db_get_or_create_user_with_id(
            db,
            user_id=AUTH_DISABLED_USER_ID,
            cognito_sub=AUTH_DISABLED_SUB,
            email=None,
        )

    return db_get_or_create_user_by_cognito_sub(
        db,
        cognito_sub=identity.cognito_sub,
        email=identity.email,
    )
