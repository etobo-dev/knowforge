from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from api.auth.deps import get_authenticated_identity
from api.auth.identity import AuthenticatedIdentity
from db.models import User
from db.repositories.users import db_get_or_create_user_by_cognito_sub
from db.session import get_db


def get_current_app_user(
    identity: Annotated[AuthenticatedIdentity, Depends(get_authenticated_identity)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    return db_get_or_create_user_by_cognito_sub(
        db,
        cognito_sub=identity.cognito_sub,
        email=identity.email,
    )
