from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.models import User


def db_get_user_by_cognito_sub(db: Session, *, cognito_sub: str) -> User | None:
    return db.query(User).filter(User.cognito_sub == cognito_sub).one_or_none()


def db_get_or_create_user_by_cognito_sub(
    db: Session,
    *,
    cognito_sub: str,
    email: str | None,
) -> User:
    normalized_sub = cognito_sub.strip()
    if not normalized_sub:
        raise ValueError("cognito_sub must not be empty")

    existing = db_get_user_by_cognito_sub(db, cognito_sub=normalized_sub)
    if existing is not None:
        return _maybe_update_email(db, user=existing, email=email)

    user = User(cognito_sub=normalized_sub, email=email)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raced = db_get_user_by_cognito_sub(db, cognito_sub=normalized_sub)
        if raced is None:
            raise
        return _maybe_update_email(db, user=raced, email=email)

    db.refresh(user)
    return user


def db_get_or_create_user_with_id(
    db: Session,
    *,
    user_id: UUID,
    cognito_sub: str,
    email: str | None = None,
) -> User:
    """Get-or-create a user with a fixed primary key (e.g. AUTH_DISABLED local user)."""
    normalized_sub = cognito_sub.strip()
    if not normalized_sub:
        raise ValueError("cognito_sub must not be empty")

    existing = db_get_user_by_cognito_sub(db, cognito_sub=normalized_sub)
    if existing is not None:
        return _maybe_update_email(db, user=existing, email=email)

    user = User(id=user_id, cognito_sub=normalized_sub, email=email)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raced = db_get_user_by_cognito_sub(db, cognito_sub=normalized_sub)
        if raced is not None:
            return _maybe_update_email(db, user=raced, email=email)
        raise

    db.refresh(user)
    return user


def _maybe_update_email(
    db: Session,
    *,
    user: User,
    email: str | None,
) -> User:
    if email is None or user.email == email:
        return user

    user.email = email
    db.commit()
    db.refresh(user)
    return user
