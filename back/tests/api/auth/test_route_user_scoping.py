from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.auth import get_current_app_user
from api.main import app
from db.factories.documents import build_document
from db.models import User
from db.repositories.chats import db_create_chat
from db.repositories.documents import db_persist_new_document


def test_documents_are_isolated_per_app_user(
    client: TestClient,
    db_session: Session,
) -> None:
    owner = User(cognito_sub="owner-sub", email="owner@example.com")
    other = User(cognito_sub="other-sub", email="other@example.com")
    db_session.add_all([owner, other])
    db_session.commit()

    document = build_document(
        user_id=owner.id,
        filename="owner.txt",
        mime_type="text/plain",
        size_bytes=4,
        content_hash="owner-hash",
    )
    db_persist_new_document(db_session, document)
    db_session.commit()

    app.dependency_overrides[get_current_app_user] = lambda: other
    try:
        other_list = client.get("/api/documents")
        other_get = client.get(f"/api/documents/{document.id}")
    finally:
        app.dependency_overrides.pop(get_current_app_user, None)

    assert other_list.status_code == 200
    assert other_list.json() == []
    assert other_get.status_code == 404

    app.dependency_overrides[get_current_app_user] = lambda: owner
    try:
        owner_list = client.get("/api/documents")
        owner_get = client.get(f"/api/documents/{document.id}")
    finally:
        app.dependency_overrides.pop(get_current_app_user, None)

    assert owner_list.status_code == 200
    assert len(owner_list.json()) == 1
    assert owner_list.json()[0]["id"] == str(document.id)
    assert owner_get.status_code == 200


def test_chats_are_isolated_per_app_user(
    client: TestClient,
    db_session: Session,
) -> None:
    owner = User(cognito_sub="chat-owner-sub", email="owner@example.com")
    other = User(cognito_sub="chat-other-sub", email="other@example.com")
    db_session.add_all([owner, other])
    db_session.commit()

    chat = db_create_chat(db_session, owner.id, title="Owner chat")

    app.dependency_overrides[get_current_app_user] = lambda: other
    try:
        other_list = client.get("/api/chats")
        other_get = client.get(f"/api/chats/{chat.id}")
    finally:
        app.dependency_overrides.pop(get_current_app_user, None)

    assert other_list.status_code == 200
    assert other_list.json() == []
    assert other_get.status_code == 404

    app.dependency_overrides[get_current_app_user] = lambda: owner
    try:
        owner_list = client.get("/api/chats")
        owner_get = client.get(f"/api/chats/{chat.id}")
    finally:
        app.dependency_overrides.pop(get_current_app_user, None)

    assert owner_list.status_code == 200
    assert len(owner_list.json()) == 1
    assert owner_list.json()[0]["id"] == str(chat.id)
    assert owner_get.status_code == 200
