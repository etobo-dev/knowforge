import pytest

from config.env import get_env, get_env_or


def test_get_env_returns_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEST_ENV_KEY", "value")
    assert get_env(key="TEST_ENV_KEY") == "value"


def test_get_env_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TEST_ENV_KEY", raising=False)
    with pytest.raises(ValueError, match="TEST_ENV_KEY"):
        get_env(key="TEST_ENV_KEY")


def test_get_env_or_returns_default_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("TEST_OPTIONAL_ENV_KEY", raising=False)
    assert get_env_or(key="TEST_OPTIONAL_ENV_KEY", default="fallback") == "fallback"
