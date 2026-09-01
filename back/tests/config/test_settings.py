import pytest

from config import get_settings, load_settings
from config.settings import (
    DEFAULT_ALLOWED_MIME_TYPES,
    DEFAULT_CHAT_MODEL,
    DEFAULT_CHAT_TURNS_ORG_DAILY,
    DEFAULT_CHAT_TURNS_USER_DAILY,
    DEFAULT_DOCUMENTS_ORG_DAILY,
    DEFAULT_DOCUMENTS_USER_DAILY,
    DEFAULT_EMBEDDING_DIMENSION,
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_EMBEDDING_TOKENS_ORG_DAILY,
    DEFAULT_EMBEDDING_TOKENS_USER_DAILY,
    DEFAULT_IMAGE_INDEX_DETAIL,
    DEFAULT_IMAGE_SEARCH_DESCRIPTION_PROMPT,
    DEFAULT_IMAGE_VECTOR_TABLE_NAME,
    DEFAULT_MAX_FILE_SIZE,
    DEFAULT_SOFT_DELETE_RETENTION_DAYS,
    DEFAULT_TOP_K,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHAT_IMAGE_DETAIL,
    DEFAULT_CONTENT_KIND_IMAGE,
    DEFAULT_CONTENT_KIND_TEXT,
    DEFAULT_VISION_MODEL,
    DEFAULT_VECTOR_TABLE_NAME,
)
from rag.llama_settings import configure_llama_index


def test_load_settings_exposes_expected_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("S3_BUCKET", "knowforge-documents-bucket")
    monkeypatch.setenv("S3_REGION", "us-east-1")

    settings = load_settings()

    assert settings.s3_bucket == "knowforge-documents-bucket"
    assert settings.s3_region == "us-east-1"
    assert settings.embedding_model == DEFAULT_EMBEDDING_MODEL
    assert settings.embedding_dimension == DEFAULT_EMBEDDING_DIMENSION
    assert settings.vector_table_name == DEFAULT_VECTOR_TABLE_NAME
    assert settings.image_vector_table_name == DEFAULT_IMAGE_VECTOR_TABLE_NAME
    assert settings.vision_model == DEFAULT_VISION_MODEL
    assert settings.chat_model == DEFAULT_CHAT_MODEL
    assert settings.image_index_detail == DEFAULT_IMAGE_INDEX_DETAIL
    assert settings.chat_image_detail == DEFAULT_CHAT_IMAGE_DETAIL
    assert settings.content_kind_image == DEFAULT_CONTENT_KIND_IMAGE
    assert settings.content_kind_text == DEFAULT_CONTENT_KIND_TEXT
    assert (
        settings.image_search_description_prompt
        == DEFAULT_IMAGE_SEARCH_DESCRIPTION_PROMPT
    )
    assert settings.top_k == DEFAULT_TOP_K
    assert settings.chunk_size == DEFAULT_CHUNK_SIZE
    assert settings.chunk_overlap == DEFAULT_CHUNK_OVERLAP
    assert settings.allowed_mime_types == DEFAULT_ALLOWED_MIME_TYPES
    assert settings.max_file_size == DEFAULT_MAX_FILE_SIZE


def test_load_settings_reads_openai_api_key_from_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "custom-key")

    settings = load_settings()

    assert settings.openai_api_key == "custom-key"


def test_load_settings_requires_s3_bucket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.delenv("S3_BUCKET", raising=False)

    with pytest.raises(ValueError, match="S3_BUCKET"):
        load_settings()


def test_load_settings_reads_s3_from_env(
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


def test_load_settings_requires_auth_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.delenv("AUTH_DISABLED", raising=False)

    with pytest.raises(ValueError, match="AUTH_DISABLED"):
        load_settings()


def test_load_settings_requires_cognito_user_pool_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("AUTH_DISABLED", "true")
    monkeypatch.delenv("COGNITO_USER_POOL_ID", raising=False)

    with pytest.raises(ValueError, match="COGNITO_USER_POOL_ID"):
        load_settings()


def test_load_settings_reads_cognito_and_auth_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("AUTH_DISABLED", "false")
    monkeypatch.setenv("COGNITO_USER_POOL_ID", "us-east-1_Example")
    monkeypatch.setenv("COGNITO_APP_CLIENT_ID", "exampleclientid")
    monkeypatch.setenv("COGNITO_REGION", "us-east-1")

    settings = load_settings()

    assert settings.auth_disabled is False
    assert settings.cognito_user_pool_id == "us-east-1_Example"
    assert settings.cognito_app_client_id == "exampleclientid"
    assert settings.cognito_region == "us-east-1"
    assert (
        settings.cognito_issuer_url
        == "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_Example"
    )


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


def test_allowed_mime_types_include_pdf_and_images() -> None:
    settings = load_settings()

    assert settings.allowed_mime_types == DEFAULT_ALLOWED_MIME_TYPES
    assert "application/pdf" in settings.allowed_mime_types
    assert "image/png" in settings.allowed_mime_types


def test_llama_settings_uses_central_chat_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import config.settings as settings_module
    import rag.llama_settings as llama_settings_module

    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setattr(settings_module, "DEFAULT_CHAT_MODEL", "gpt-4o")
    llama_settings_module._configured = False

    import config as config_package

    config_package._settings = None

    configure_llama_index()

    from llama_index.core import Settings

    assert Settings.llm.model == "gpt-4o"
