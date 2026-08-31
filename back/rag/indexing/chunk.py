from functools import lru_cache

from llama_index.core.node_parser import SentenceSplitter

from config import get_settings


@lru_cache
def _get_splitter() -> SentenceSplitter:
    settings = get_settings()
    return SentenceSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )


def chunk_text(text: str) -> list[str]:
    stripped = text.strip()
    chunks = _get_splitter().split_text(stripped)

    if not chunks:
        raise ValueError("Document has no extractable text")

    return chunks
