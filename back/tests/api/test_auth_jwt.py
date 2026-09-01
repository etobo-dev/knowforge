from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

from api.auth.jwt import verify_cognito_access_token
from config.settings import Settings, DailyQuotaLimits


def _rsa_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _settings(*, client_id: str = "test-client") -> Settings:
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
        auth_disabled=False,
        cognito_user_pool_id="us-east-1_TestPool",
        cognito_app_client_id=client_id,
        cognito_region="us-east-1",
        quotas=DailyQuotaLimits(),
    )


def _access_token(
    *,
    private_key: rsa.RSAPrivateKey,
    settings: Settings,
    token_use: str = "access",
    client_id: str | None = None,
    sub: str = "cognito-sub-1",
    email: str | None = "user@example.com",
) -> str:
    now = datetime.now(timezone.utc)
    claims: dict[str, object] = {
        "sub": sub,
        "iss": settings.cognito_issuer_url,
        "token_use": token_use,
        "client_id": client_id if client_id is not None else settings.cognito_app_client_id,
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }
    if email is not None:
        claims["email"] = email
    return jwt.encode(claims, private_key, algorithm="RS256")


def test_verify_cognito_access_token_returns_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key = _rsa_key()
    settings = _settings()
    token = _access_token(private_key=private_key, settings=settings)

    signing_key = MagicMock()
    signing_key.key = private_key.public_key()
    monkeypatch.setattr(
        "api.auth.jwt.PyJWKClient.get_signing_key_from_jwt",
        lambda self, token: signing_key,
    )

    identity = verify_cognito_access_token(settings=settings, access_token=token)

    assert identity.cognito_sub == "cognito-sub-1"
    assert identity.email == "user@example.com"


def test_verify_cognito_access_token_rejects_wrong_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key = _rsa_key()
    settings = _settings()
    token = _access_token(
        private_key=private_key,
        settings=settings,
        client_id="other-client",
    )

    signing_key = MagicMock()
    signing_key.key = private_key.public_key()
    monkeypatch.setattr(
        "api.auth.jwt.PyJWKClient.get_signing_key_from_jwt",
        lambda self, token: signing_key,
    )

    with pytest.raises(HTTPException) as exc_info:
        verify_cognito_access_token(settings=settings, access_token=token)

    assert exc_info.value.status_code == 401


def test_verify_cognito_access_token_rejects_id_token_use(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    private_key = _rsa_key()
    settings = _settings()
    token = _access_token(
        private_key=private_key,
        settings=settings,
        token_use="id",
    )

    signing_key = MagicMock()
    signing_key.key = private_key.public_key()
    monkeypatch.setattr(
        "api.auth.jwt.PyJWKClient.get_signing_key_from_jwt",
        lambda self, token: signing_key,
    )

    with pytest.raises(HTTPException) as exc_info:
        verify_cognito_access_token(settings=settings, access_token=token)

    assert exc_info.value.status_code == 401
