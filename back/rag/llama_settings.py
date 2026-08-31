from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

from config import get_settings

_configured = False


def configure_llama_index() -> None:
    global _configured
    if _configured:
        return

    settings = get_settings()

    Settings.embed_model = OpenAIEmbedding(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )
    Settings.llm = OpenAI(
        model=settings.chat_model,
        api_key=settings.openai_api_key,
    )
    _configured = True


def get_vision_llm(*, detail: str) -> OpenAI:
    configure_llama_index()

    settings = get_settings()

    return OpenAI(
        model=settings.vision_model,
        api_key=settings.openai_api_key,
        model_kwargs={"detail": detail},
    )
