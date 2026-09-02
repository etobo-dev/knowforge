from fastapi.testclient import TestClient


def test_protected_documents_require_auth_when_enabled(
    client: TestClient,
    monkeypatch,
) -> None:
    import config as config_package
    from config import get_settings

    monkeypatch.setenv("AUTH_DISABLED", "false")
    config_package._settings = None
    settings = get_settings()
    assert settings.auth_disabled is False

    response = client.get("/api/documents")

    assert response.status_code == 401

    monkeypatch.setenv("AUTH_DISABLED", "true")
    config_package._settings = None


def test_protected_chats_require_auth_when_enabled(
    client: TestClient,
    monkeypatch,
) -> None:
    import config as config_package
    from config import get_settings

    monkeypatch.setenv("AUTH_DISABLED", "false")
    config_package._settings = None
    assert get_settings().auth_disabled is False

    response = client.get("/api/chats")

    assert response.status_code == 401

    monkeypatch.setenv("AUTH_DISABLED", "true")
    config_package._settings = None
