import pytest

from config.env import get_bool_env, get_env


def test_get_env_returns_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEST_ENV_KEY", "value")
    assert get_env(key="TEST_ENV_KEY") == "value"


def test_get_env_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TEST_ENV_KEY", raising=False)
    with pytest.raises(ValueError, match="TEST_ENV_KEY"):
        get_env(key="TEST_ENV_KEY")


def test_get_bool_env_returns_true_and_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TEST_BOOL", "true")
    assert get_bool_env(key="TEST_BOOL") is True
    monkeypatch.setenv("TEST_BOOL", "false")
    assert get_bool_env(key="TEST_BOOL") is False


def test_get_bool_env_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TEST_BOOL", raising=False)
    with pytest.raises(ValueError, match="TEST_BOOL"):
        get_bool_env(key="TEST_BOOL")


def test_get_bool_env_rejects_invalid_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TEST_BOOL", "yes")
    with pytest.raises(ValueError, match="TEST_BOOL"):
        get_bool_env(key="TEST_BOOL")
