import pytest
from sqlalchemy.orm import Session

from api.auth.app_user import get_current_app_user
from api.auth.identity import AuthenticatedIdentity
from db.models import User


def test_get_current_app_user_creates_user_from_cognito_identity(
    db_session: Session,
) -> None:
    user = get_current_app_user(
        identity=AuthenticatedIdentity(
            cognito_sub="cognito-sub-1",
            email="user@example.com",
        ),
        db=db_session,
    )

    assert user.cognito_sub == "cognito-sub-1"
    assert user.email == "user@example.com"


def test_get_current_app_user_reuses_cognito_user(
    db_session: Session,
) -> None:
    first = get_current_app_user(
        identity=AuthenticatedIdentity(
            cognito_sub="cognito-sub-reuse",
            email="first@example.com",
        ),
        db=db_session,
    )
    second = get_current_app_user(
        identity=AuthenticatedIdentity(
            cognito_sub="cognito-sub-reuse",
            email="first@example.com",
        ),
        db=db_session,
    )

    assert first.id == second.id
    assert db_session.query(User).count() == 1


def test_get_current_app_user_updates_email_from_identity(
    db_session: Session,
) -> None:
    first = get_current_app_user(
        identity=AuthenticatedIdentity(cognito_sub="email-sub", email=None),
        db=db_session,
    )
    second = get_current_app_user(
        identity=AuthenticatedIdentity(
            cognito_sub="email-sub",
            email="later@example.com",
        ),
        db=db_session,
    )

    assert first.id == second.id
    assert second.email == "later@example.com"


def test_get_current_app_user_does_not_clear_email_with_none(
    db_session: Session,
) -> None:
    first = get_current_app_user(
        identity=AuthenticatedIdentity(
            cognito_sub="keep-email-sub",
            email="keep@example.com",
        ),
        db=db_session,
    )
    second = get_current_app_user(
        identity=AuthenticatedIdentity(cognito_sub="keep-email-sub", email=None),
        db=db_session,
    )

    assert first.id == second.id
    assert second.email == "keep@example.com"


def test_get_current_app_user_isolates_different_cognito_subs(
    db_session: Session,
) -> None:
    first = get_current_app_user(
        identity=AuthenticatedIdentity(cognito_sub="sub-a", email="a@example.com"),
        db=db_session,
    )
    second = get_current_app_user(
        identity=AuthenticatedIdentity(cognito_sub="sub-b", email="b@example.com"),
        db=db_session,
    )

    assert first.id != second.id
    assert db_session.query(User).count() == 2


def test_get_current_app_user_rejects_empty_cognito_sub(
    db_session: Session,
) -> None:
    with pytest.raises(ValueError, match="cognito_sub must not be empty"):
        get_current_app_user(
            identity=AuthenticatedIdentity(cognito_sub="   ", email="x@example.com"),
            db=db_session,
        )
