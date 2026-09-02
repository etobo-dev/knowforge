from uuid import UUID, uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.models import Chat, Message, MessageRole, MessageSource, User


def test_user_model_constructs_with_email() -> None:
    user = User(cognito_sub="cognito-sub-1", email="user@example.com")

    assert user.cognito_sub == "cognito-sub-1"
    assert user.email == "user@example.com"


def test_user_model_constructs_without_email() -> None:
    user = User(cognito_sub="cognito-sub-2")

    assert user.cognito_sub == "cognito-sub-2"
    assert user.email is None


def test_user_persists_and_assigns_id(db_session: Session) -> None:
    user = User(cognito_sub="cognito-sub-persist", email="persist@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert isinstance(user.id, UUID)
    assert user.created_at is not None
    assert user.updated_at is not None


def test_user_round_trip_by_cognito_sub(db_session: Session) -> None:
    user = User(cognito_sub="cognito-sub-lookup", email="lookup@example.com")
    db_session.add(user)
    db_session.commit()

    found = (
        db_session.query(User)
        .filter(User.cognito_sub == "cognito-sub-lookup")
        .one_or_none()
    )

    assert found is not None
    assert found.id == user.id
    assert found.email == "lookup@example.com"


def test_user_email_can_be_null_when_persisted(db_session: Session) -> None:
    user = User(cognito_sub="cognito-sub-no-email", email=None)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.email is None


def test_user_rejects_null_cognito_sub(db_session: Session) -> None:
    user = User(cognito_sub=None, email="missing-sub@example.com")  # type: ignore[arg-type]
    db_session.add(user)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_user_cognito_sub_must_be_unique(db_session: Session) -> None:
    db_session.add(User(cognito_sub="shared-sub", email="first@example.com"))
    db_session.commit()

    db_session.add(User(cognito_sub="shared-sub", email="second@example.com"))
    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()


def test_user_email_is_not_unique(db_session: Session) -> None:
    shared_email = "same@example.com"
    first = User(cognito_sub="sub-a", email=shared_email)
    second = User(cognito_sub="sub-b", email=shared_email)
    db_session.add_all([first, second])
    db_session.commit()

    assert first.id != second.id
    assert first.email == second.email == shared_email


def test_user_accepts_explicit_id(db_session: Session) -> None:
    user_id = uuid4()
    user = User(
        id=user_id,
        cognito_sub="cognito-sub-explicit-id",
        email="explicit@example.com",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id == user_id


def test_chat_message_and_source_models_construct() -> None:
    chat = Chat(title="Support")
    message = Message(role=MessageRole.USER, content="Hello")
    source = MessageSource(score=0.9, quoted_text="snippet")

    chat.messages.append(message)
    message.sources.append(source)

    assert chat.title == "Support"
    assert message.role == MessageRole.USER
    assert source.score == 0.9
