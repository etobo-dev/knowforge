import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from api.auth.deps import AUTH_DISABLED_SUB, get_authenticated_identity
from api.auth.identity import AuthenticatedIdentity
from config.settings import DailyQuotaLimits, Settings


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


def test_get_authenticated_identity_bypasses_when_auth_disabled() -> None:
    identity = get_authenticated_identity(
        credentials=None,
        settings=_settings(auth_disabled=True),
    )

    assert identity.cognito_sub == AUTH_DISABLED_SUB
    assert identity.email is None


def test_get_authenticated_identity_requires_bearer_when_auth_enabled() -> None:
    with pytest.raises(HTTPException) as exc_info:
        get_authenticated_identity(
            credentials=None,
            settings=_settings(auth_disabled=False),
        )

    assert exc_info.value.status_code == 401


def test_get_authenticated_identity_verifies_bearer_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "api.auth.deps.verify_cognito_access_token",
        lambda **kwargs: AuthenticatedIdentity(
            cognito_sub="sub-from-token",
            email="a@b.com",
        ),
    )

    identity = get_authenticated_identity(
        credentials=HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="token",
        ),
        settings=_settings(auth_disabled=False),
    )

    assert identity.cognito_sub == "sub-from-token"
    assert identity.email == "a@b.com"
