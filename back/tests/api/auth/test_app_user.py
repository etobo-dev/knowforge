from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from api.auth.app_user import (
    AUTH_DISABLED_USER_ID,
    get_current_app_user,
)
from api.auth.deps import AUTH_DISABLED_SUB
from api.auth.identity import AuthenticatedIdentity
from config.settings import DailyQuotaLimits, Settings
from db.models import User
from db.repositories.users import db_get_user_by_cognito_sub


def _settings(*, auth_disabled: bool) -> Settings:
    return Settings(
        s3_bucket="bucket",
        s3_region="us-east-1",
        openai_api_key="key",
        embedding_model="model",
        embedding_dimension=1536,
        vector_table_name="vectors",
        image_vector_table_name="image_vectors",
        vision_model="vision",
        chat_model="chat",
        image_index_detail="low",
        chat_image_detail="high",
        content_kind_image="image",
        content_kind_text="text",
        image_search_description_prompt="prompt",
        top_k=5,
        chunk_size=1024,
        chunk_overlap=200,
        allowed_mime_types=frozenset({"application/pdf"}),
        max_file_size=1024,
        auth_disabled=auth_disabled,
        cognito_user_pool_id="us-east-1_TestPool",
        cognito_app_client_id="test-client",
        cognito_region="us-east-1",
        quotas=DailyQuotaLimits(),
    )


def test_get_current_app_user_creates_auth_disabled_user(
    db_session: Session,
) -> None:
    user = get_current_app_user(
        identity=AuthenticatedIdentity(cognito_sub=AUTH_DISABLED_SUB, email=None),
        db=db_session,
        settings=_settings(auth_disabled=True),
    )

    assert user.id == AUTH_DISABLED_USER_ID
    assert user.cognito_sub == AUTH_DISABLED_SUB
    assert user.email is None


def test_get_current_app_user_reuses_auth_disabled_user(
    db_session: Session,
) -> None:
    first = get_current_app_user(
        identity=AuthenticatedIdentity(cognito_sub=AUTH_DISABLED_SUB, email=None),
        db=db_session,
        settings=_settings(auth_disabled=True),
    )
    second = get_current_app_user(
        identity=AuthenticatedIdentity(cognito_sub=AUTH_DISABLED_SUB, email=None),
        db=db_session,
        settings=_settings(auth_disabled=True),
    )

    assert first.id == second.id == AUTH_DISABLED_USER_ID
    assert db_session.query(User).count() == 1


def test_get_current_app_user_ignores_identity_when_auth_disabled(
    db_session: Session,
) -> None:
    user = get_current_app_user(
        identity=AuthenticatedIdentity(
            cognito_sub="should-be-ignored",
            email="ignored@example.com",
        ),
        db=db_session,
        settings=_settings(auth_disabled=True),
    )

    assert user.id == AUTH_DISABLED_USER_ID
    assert user.cognito_sub == AUTH_DISABLED_SUB
    assert user.email is None


def test_get_current_app_user_keeps_existing_auth_disabled_row(
    db_session: Session,
) -> None:
    existing_id = uuid4()
    db_session.add(
        User(
            id=existing_id,
            cognito_sub=AUTH_DISABLED_SUB,
            email=None,
        )
    )
    db_session.commit()

    user = get_current_app_user(
        identity=AuthenticatedIdentity(cognito_sub=AUTH_DISABLED_SUB, email=None),
        db=db_session,
        settings=_settings(auth_disabled=True),
    )

    assert user.id == existing_id
    assert user.cognito_sub == AUTH_DISABLED_SUB


def test_get_current_app_user_recovers_auth_disabled_race(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_session.add(
        User(
            id=AUTH_DISABLED_USER_ID,
            cognito_sub=AUTH_DISABLED_SUB,
            email=None,
        )
    )
    db_session.commit()

    calls = {"count": 0}
    real_get = db_get_user_by_cognito_sub

    def fake_get(db: Session, *, cognito_sub: str) -> User | None:
        calls["count"] += 1
        if calls["count"] == 1:
            return None
        return real_get(db, cognito_sub=cognito_sub)

    monkeypatch.setattr(
        "db.repositories.users.db_get_user_by_cognito_sub",
        fake_get,
    )

    user = get_current_app_user(
        identity=AuthenticatedIdentity(cognito_sub=AUTH_DISABLED_SUB, email=None),
        db=db_session,
        settings=_settings(auth_disabled=True),
    )

    assert user.id == AUTH_DISABLED_USER_ID
    assert db_session.query(User).count() == 1


def test_get_current_app_user_creates_user_from_cognito_identity(
    db_session: Session,
) -> None:
    user = get_current_app_user(
        identity=AuthenticatedIdentity(
            cognito_sub="cognito-sub-1",
            email="user@example.com",
        ),
        db=db_session,
        settings=_settings(auth_disabled=False),
    )

    assert user.cognito_sub == "cognito-sub-1"
    assert user.email == "user@example.com"
    assert user.id != AUTH_DISABLED_USER_ID


def test_get_current_app_user_reuses_cognito_user(
    db_session: Session,
) -> None:
    first = get_current_app_user(
        identity=AuthenticatedIdentity(
            cognito_sub="cognito-sub-reuse",
            email="first@example.com",
        ),
        db=db_session,
        settings=_settings(auth_disabled=False),
    )
    second = get_current_app_user(
        identity=AuthenticatedIdentity(
            cognito_sub="cognito-sub-reuse",
            email="first@example.com",
        ),
        db=db_session,
        settings=_settings(auth_disabled=False),
    )

    assert first.id == second.id
    assert db_session.query(User).count() == 1


def test_get_current_app_user_updates_email_from_identity(
    db_session: Session,
) -> None:
    first = get_current_app_user(
        identity=AuthenticatedIdentity(cognito_sub="email-sub", email=None),
        db=db_session,
        settings=_settings(auth_disabled=False),
    )
    second = get_current_app_user(
        identity=AuthenticatedIdentity(
            cognito_sub="email-sub",
            email="later@example.com",
        ),
        db=db_session,
        settings=_settings(auth_disabled=False),
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
        settings=_settings(auth_disabled=False),
    )
    second = get_current_app_user(
        identity=AuthenticatedIdentity(cognito_sub="keep-email-sub", email=None),
        db=db_session,
        settings=_settings(auth_disabled=False),
    )

    assert first.id == second.id
    assert second.email == "keep@example.com"


def test_get_current_app_user_isolates_different_cognito_subs(
    db_session: Session,
) -> None:
    first = get_current_app_user(
        identity=AuthenticatedIdentity(cognito_sub="sub-a", email="a@example.com"),
        db=db_session,
        settings=_settings(auth_disabled=False),
    )
    second = get_current_app_user(
        identity=AuthenticatedIdentity(cognito_sub="sub-b", email="b@example.com"),
        db=db_session,
        settings=_settings(auth_disabled=False),
    )

    assert first.id != second.id
    assert db_session.query(User).count() == 2


def test_get_current_app_user_rejects_empty_cognito_sub_when_auth_enabled(
    db_session: Session,
) -> None:
    with pytest.raises(ValueError, match="cognito_sub must not be empty"):
        get_current_app_user(
            identity=AuthenticatedIdentity(cognito_sub="   ", email="x@example.com"),
            db=db_session,
            settings=_settings(auth_disabled=False),
        )
