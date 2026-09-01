from dataclasses import dataclass, field

from config.env import get_bool_env, get_env

DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_EMBEDDING_DIMENSION = 1536
DEFAULT_VECTOR_TABLE_NAME = "knowforge_vectors"
DEFAULT_IMAGE_VECTOR_TABLE_NAME = "knowforge_vectors_image"
DEFAULT_VISION_MODEL = "gpt-4o-mini"
DEFAULT_CHAT_MODEL = "gpt-4o-mini"
DEFAULT_IMAGE_INDEX_DETAIL = "low"
DEFAULT_CHAT_IMAGE_DETAIL = "high"
DEFAULT_CONTENT_KIND_IMAGE = "image"
DEFAULT_CONTENT_KIND_TEXT = "text"
DEFAULT_IMAGE_SEARCH_DESCRIPTION_PROMPT = (
    "Describe this image in dense, search-friendly prose for retrieval. "
    "Include visible text, objects, layout, colors, and any data or charts. "
    "Do not use markdown or bullet lists."
)
DEFAULT_TOP_K = 5
DEFAULT_CHUNK_SIZE = 1024
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_MAX_FILE_SIZE = 25 * 1024 * 1024

DEFAULT_ALLOWED_MIME_TYPES = frozenset(
    {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/markdown",
        "image/png",
        "image/jpeg",
    }
)

DEFAULT_CHAT_TURNS_USER_DAILY = 30
DEFAULT_CHAT_TURNS_ORG_DAILY = 200
DEFAULT_DOCUMENTS_USER_DAILY = 20
DEFAULT_DOCUMENTS_ORG_DAILY = 100
DEFAULT_EMBEDDING_TOKENS_USER_DAILY = 200_000
DEFAULT_EMBEDDING_TOKENS_ORG_DAILY = 1_000_000

DEFAULT_SOFT_DELETE_RETENTION_DAYS = 30

DEFAULT_S3_BUCKET = "knowforge-documents-bucket"
DEFAULT_S3_REGION = "us-east-1"


@dataclass(frozen=True)
class DailyQuotaLimits:
    chat_turns_user: int = DEFAULT_CHAT_TURNS_USER_DAILY
    chat_turns_org: int = DEFAULT_CHAT_TURNS_ORG_DAILY
    documents_user: int = DEFAULT_DOCUMENTS_USER_DAILY
    documents_org: int = DEFAULT_DOCUMENTS_ORG_DAILY
    embedding_tokens_user: int = DEFAULT_EMBEDDING_TOKENS_USER_DAILY
    embedding_tokens_org: int = DEFAULT_EMBEDDING_TOKENS_ORG_DAILY


@dataclass(frozen=True)
class Settings:
    s3_bucket: str
    s3_region: str
    openai_api_key: str
    embedding_model: str
    embedding_dimension: int
    vector_table_name: str
    image_vector_table_name: str
    vision_model: str
    chat_model: str
    image_index_detail: str
    chat_image_detail: str
    content_kind_image: str
    content_kind_text: str
    image_search_description_prompt: str
    top_k: int
    chunk_size: int
    chunk_overlap: int
    allowed_mime_types: frozenset[str]
    max_file_size: int
    auth_disabled: bool
    cognito_user_pool_id: str
    cognito_app_client_id: str
    cognito_region: str
    quotas: DailyQuotaLimits = field(default_factory=DailyQuotaLimits)
    soft_delete_retention_days: int = DEFAULT_SOFT_DELETE_RETENTION_DAYS

    @property
    def cognito_issuer_url(self) -> str:
        return (
            f"https://cognito-idp.{self.cognito_region}.amazonaws.com/"
            f"{self.cognito_user_pool_id}"
        )


def load_settings() -> Settings:
    return Settings(
        s3_bucket=DEFAULT_S3_BUCKET,
        s3_region=DEFAULT_S3_REGION,
        openai_api_key=get_env(key="OPENAI_API_KEY"),
        embedding_model=DEFAULT_EMBEDDING_MODEL,
        embedding_dimension=DEFAULT_EMBEDDING_DIMENSION,
        vector_table_name=DEFAULT_VECTOR_TABLE_NAME,
        image_vector_table_name=DEFAULT_IMAGE_VECTOR_TABLE_NAME,
        vision_model=DEFAULT_VISION_MODEL,
        chat_model=DEFAULT_CHAT_MODEL,
        image_index_detail=DEFAULT_IMAGE_INDEX_DETAIL,
        chat_image_detail=DEFAULT_CHAT_IMAGE_DETAIL,
        content_kind_image=DEFAULT_CONTENT_KIND_IMAGE,
        content_kind_text=DEFAULT_CONTENT_KIND_TEXT,
        image_search_description_prompt=DEFAULT_IMAGE_SEARCH_DESCRIPTION_PROMPT,
        top_k=DEFAULT_TOP_K,
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
        allowed_mime_types=DEFAULT_ALLOWED_MIME_TYPES,
        max_file_size=DEFAULT_MAX_FILE_SIZE,
        auth_disabled=get_bool_env(key="AUTH_DISABLED"),
        cognito_user_pool_id=get_env(key="COGNITO_USER_POOL_ID"),
        cognito_app_client_id=get_env(key="COGNITO_APP_CLIENT_ID"),
        cognito_region=get_env(key="COGNITO_REGION"),
    )
