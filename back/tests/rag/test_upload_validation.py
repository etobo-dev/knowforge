import pytest

from config import get_settings
from rag.upload import _check_content_type, _check_file_size


def test_check_content_type_accepts_allowed_mime() -> None:
    _check_content_type("text/plain")
    _check_content_type("image/png")


def test_check_content_type_rejects_unknown_mime() -> None:
    with pytest.raises(ValueError, match="Unsupported file type"):
        _check_content_type("application/zip")


def test_check_file_size_accepts_within_limit() -> None:
    settings = get_settings()
    _check_file_size(settings.max_file_size)


def test_check_file_size_rejects_oversized_file() -> None:
    settings = get_settings()
    with pytest.raises(ValueError, match="File too large"):
        _check_file_size(settings.max_file_size + 1)
