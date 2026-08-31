import pytest

from config import get_settings, load_settings
from config.settings import (
    DEFAULT_ALLOWED_MIME_TYPES,
    DEFAULT_CHAT_TURNS_ORG_DAILY,
    DEFAULT_CHAT_TURNS_USER_DAILY,
    DEFAULT_DOCUMENTS_ORG_DAILY,
    DEFAULT_DOCUMENTS_USER_DAILY,
    DEFAULT_EMBEDDING_TOKENS_ORG_DAILY,
    DEFAULT_EMBEDDING_TOKENS_USER_DAILY,
    DEFAULT_SOFT_DELETE_RETENTION_DAYS,
)
from rag.config import Config


def test_load_settings_matches_rag_config_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.delenv("S3_BUCKET", raising=False)
    monkeypatch.delenv("S3_REGION", raising=False)

    settings = load_settings()

    assert settings.s3_bucket == Config.S3_BUCKET
    assert settings.s3_region == Config.S3_REGION
    assert settings.embedding_model == Config.EMBEDDING_MODEL
    assert settings.embedding_dimension == Config.EMBEDDING_DIMENSION
    assert settings.vector_table_name == Config.VECTOR_TABLE_NAME
    assert settings.image_vector_table_name == Config.IMAGE_VECTOR_TABLE_NAME
    assert settings.vision_model == Config.VISION_MODEL
    assert settings.chat_model == Config.CHAT_MODEL
    assert settings.image_index_detail == Config.IMAGE_INDEX_DETAIL
    assert settings.chat_image_detail == Config.CHAT_IMAGE_DETAIL
    assert settings.content_kind_image == Config.CONTENT_KIND_IMAGE
    assert settings.content_kind_text == Config.CONTENT_KIND_TEXT
    assert settings.image_search_description_prompt == Config.IMAGE_SEARCH_DESCRIPTION_PROMPT
    assert settings.top_k == Config.TOP_K
    assert settings.chunk_size == Config.CHUNK_SIZE
    assert settings.chunk_overlap == Config.CHUNK_OVERLAP
    assert settings.allowed_mime_types == frozenset(Config.ALLOWED_MIME_TYPES)
    assert settings.max_file_size == Config.MAX_FILE_SIZE


def test_load_settings_reads_openai_api_key_from_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "custom-key")

    settings = load_settings()

    assert settings.openai_api_key == "custom-key"


def test_load_settings_reads_s3_overrides_from_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("S3_BUCKET", "custom-bucket")
    monkeypatch.setenv("S3_REGION", "eu-west-1")

    settings = load_settings()

    assert settings.s3_bucket == "custom-bucket"
    assert settings.s3_region == "eu-west-1"


def test_load_settings_exposes_beta_quota_defaults() -> None:
    settings = load_settings()

    assert settings.quotas.chat_turns_user == DEFAULT_CHAT_TURNS_USER_DAILY
    assert settings.quotas.chat_turns_org == DEFAULT_CHAT_TURNS_ORG_DAILY
    assert settings.quotas.documents_user == DEFAULT_DOCUMENTS_USER_DAILY
    assert settings.quotas.documents_org == DEFAULT_DOCUMENTS_ORG_DAILY
    assert settings.quotas.embedding_tokens_user == DEFAULT_EMBEDDING_TOKENS_USER_DAILY
    assert settings.quotas.embedding_tokens_org == DEFAULT_EMBEDDING_TOKENS_ORG_DAILY


def test_load_settings_exposes_soft_delete_retention() -> None:
    settings = load_settings()

    assert settings.soft_delete_retention_days == DEFAULT_SOFT_DELETE_RETENTION_DAYS


def test_load_settings_requires_openai_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        load_settings()


def test_get_settings_returns_cached_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import config as config_package

    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    config_package._settings = None

    first = get_settings()
    second = get_settings()

    assert first is second


def test_allowed_mime_types_match_rag_config() -> None:
    settings = load_settings()

    assert settings.allowed_mime_types == DEFAULT_ALLOWED_MIME_TYPES
    assert "application/pdf" in settings.allowed_mime_types
    assert "image/png" in settings.allowed_mime_types
