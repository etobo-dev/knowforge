from fastapi.testclient import TestClient


def test_protected_documents_require_auth(client: TestClient) -> None:
    from api.auth import get_current_app_user
    from api.main import app

    app.dependency_overrides.pop(get_current_app_user, None)

    response = client.get("/api/documents")

    assert response.status_code == 401


def test_protected_chats_require_auth(client: TestClient) -> None:
    from api.auth import get_current_app_user
    from api.main import app

    app.dependency_overrides.pop(get_current_app_user, None)

    response = client.get("/api/chats")

    assert response.status_code == 401
