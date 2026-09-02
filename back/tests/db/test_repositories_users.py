from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from db.models import User
from db.repositories.users import (
    db_get_or_create_user_by_cognito_sub,
    db_get_or_create_user_with_id,
    db_get_user_by_cognito_sub,
)


def test_db_get_user_by_cognito_sub_returns_none_when_missing(
    db_session: Session,
) -> None:
    found = db_get_user_by_cognito_sub(db_session, cognito_sub="missing-sub")

    assert found is None


def test_db_get_user_by_cognito_sub_returns_existing_user(
    db_session: Session,
) -> None:
    user = User(cognito_sub="existing-sub", email="existing@example.com")
    db_session.add(user)
    db_session.commit()

    found = db_get_user_by_cognito_sub(db_session, cognito_sub="existing-sub")

    assert found is not None
    assert found.id == user.id
    assert found.email == "existing@example.com"


def test_db_get_or_create_creates_user_when_missing(db_session: Session) -> None:
    user = db_get_or_create_user_by_cognito_sub(
        db_session,
        cognito_sub="new-sub",
        email="new@example.com",
    )

    assert user.cognito_sub == "new-sub"
    assert user.email == "new@example.com"
    assert (
        db_get_user_by_cognito_sub(db_session, cognito_sub="new-sub") is not None
    )


def test_db_get_or_create_creates_user_with_null_email(db_session: Session) -> None:
    user = db_get_or_create_user_by_cognito_sub(
        db_session,
        cognito_sub="no-email-sub",
        email=None,
    )

    assert user.email is None


def test_db_get_or_create_returns_same_user_on_repeat(
    db_session: Session,
) -> None:
    first = db_get_or_create_user_by_cognito_sub(
        db_session,
        cognito_sub="repeat-sub",
        email="first@example.com",
    )
    second = db_get_or_create_user_by_cognito_sub(
        db_session,
        cognito_sub="repeat-sub",
        email="first@example.com",
    )

    assert first.id == second.id
    assert db_session.query(User).filter(User.cognito_sub == "repeat-sub").count() == 1


def test_db_get_or_create_updates_email_when_provided(
    db_session: Session,
) -> None:
    first = db_get_or_create_user_by_cognito_sub(
        db_session,
        cognito_sub="email-update-sub",
        email=None,
    )
    updated = db_get_or_create_user_by_cognito_sub(
        db_session,
        cognito_sub="email-update-sub",
        email="updated@example.com",
    )

    assert first.id == updated.id
    assert updated.email == "updated@example.com"


def test_db_get_or_create_does_not_clear_email_with_none(
    db_session: Session,
) -> None:
    first = db_get_or_create_user_by_cognito_sub(
        db_session,
        cognito_sub="keep-email-sub",
        email="keep@example.com",
    )
    second = db_get_or_create_user_by_cognito_sub(
        db_session,
        cognito_sub="keep-email-sub",
        email=None,
    )

    assert first.id == second.id
    assert second.email == "keep@example.com"


def test_db_get_or_create_strips_cognito_sub_whitespace(
    db_session: Session,
) -> None:
    user = db_get_or_create_user_by_cognito_sub(
        db_session,
        cognito_sub="  padded-sub  ",
        email="padded@example.com",
    )

    assert user.cognito_sub == "padded-sub"
    assert (
        db_get_user_by_cognito_sub(db_session, cognito_sub="padded-sub") is not None
    )


def test_db_get_or_create_rejects_empty_cognito_sub(db_session: Session) -> None:
    with pytest.raises(ValueError, match="cognito_sub must not be empty"):
        db_get_or_create_user_by_cognito_sub(
            db_session,
            cognito_sub="   ",
            email="empty@example.com",
        )


def test_db_get_or_create_rejects_blank_cognito_sub(db_session: Session) -> None:
    with pytest.raises(ValueError, match="cognito_sub must not be empty"):
        db_get_or_create_user_by_cognito_sub(
            db_session,
            cognito_sub="",
            email="blank@example.com",
        )


def test_db_get_or_create_isolates_different_cognito_subs(
    db_session: Session,
) -> None:
    first = db_get_or_create_user_by_cognito_sub(
        db_session,
        cognito_sub="sub-one",
        email="one@example.com",
    )
    second = db_get_or_create_user_by_cognito_sub(
        db_session,
        cognito_sub="sub-two",
        email="two@example.com",
    )

    assert first.id != second.id
    assert db_session.query(User).count() == 2


def test_db_get_or_create_recovers_from_concurrent_insert(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_session.add(User(cognito_sub="race-sub", email="original@example.com"))
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

    user = db_get_or_create_user_by_cognito_sub(
        db_session,
        cognito_sub="race-sub",
        email="after-race@example.com",
    )

    assert user.cognito_sub == "race-sub"
    assert user.email == "after-race@example.com"
    assert db_session.query(User).filter(User.cognito_sub == "race-sub").count() == 1


def test_db_get_or_create_user_with_id_creates_with_fixed_id(
    db_session: Session,
) -> None:
    user_id = uuid4()
    user = db_get_or_create_user_with_id(
        db_session,
        user_id=user_id,
        cognito_sub="fixed-id-sub",
        email=None,
    )

    assert user.id == user_id
    assert user.cognito_sub == "fixed-id-sub"


def test_db_get_or_create_user_with_id_reuses_existing_by_sub(
    db_session: Session,
) -> None:
    existing_id = uuid4()
    db_session.add(
        User(id=existing_id, cognito_sub="reuse-fixed-sub", email=None)
    )
    db_session.commit()

    user = db_get_or_create_user_with_id(
        db_session,
        user_id=uuid4(),
        cognito_sub="reuse-fixed-sub",
        email=None,
    )

    assert user.id == existing_id


def test_db_get_or_create_user_with_id_rejects_empty_sub(
    db_session: Session,
) -> None:
    with pytest.raises(ValueError, match="cognito_sub must not be empty"):
        db_get_or_create_user_with_id(
            db_session,
            user_id=uuid4(),
            cognito_sub="  ",
            email=None,
        )


def test_db_get_or_create_user_with_id_recovers_from_concurrent_insert(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user_id = uuid4()
    db_session.add(User(id=user_id, cognito_sub="fixed-race-sub", email=None))
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

    user = db_get_or_create_user_with_id(
        db_session,
        user_id=user_id,
        cognito_sub="fixed-race-sub",
        email=None,
    )

    assert user.id == user_id
    assert db_session.query(User).filter(User.cognito_sub == "fixed-race-sub").count() == 1
