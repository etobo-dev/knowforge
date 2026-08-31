import functools
from typing import TYPE_CHECKING, cast

import boto3

from config import get_settings
from db.models import Document

if TYPE_CHECKING:
    from types_boto3_s3 import S3Client


@functools.cache
def get_s3_client() -> "S3Client":
    # Default credential chain: env/profile locally, IAM role in Lambda.
    settings = get_settings()
    return boto3.client("s3", region_name=settings.s3_region)


def upload_document_to_s3(document: Document, content: bytes) -> None:
    settings = get_settings()
    s3 = get_s3_client()
    s3.put_object(
        Bucket=settings.s3_bucket,
        Key=document.s3_key,
        Body=content,
        ContentType=document.mime_type,
    )


def delete_object_from_s3(s3_key: str) -> None:
    settings = get_settings()
    s3 = get_s3_client()
    s3.delete_object(Bucket=settings.s3_bucket, Key=s3_key)


def _safe_attachment_filename(name: str) -> str:
    base = name.rsplit("/", maxsplit=1)[-1]
    return base.replace('"', "'")[:200]


def presigned_inline_url(
    s3_key: str,
    *,
    expires_in: int = 3600,
) -> str:
    settings = get_settings()
    s3 = get_s3_client()
    return cast(
        str,
        s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.s3_bucket,
                "Key": s3_key,
            },
            ExpiresIn=expires_in,
        ),
    )


def presigned_download_url(
    s3_key: str,
    download_filename: str,
    *,
    expires_in: int = 300,
) -> str:
    settings = get_settings()
    s3 = get_s3_client()
    disposition = (
        f'attachment; filename="{_safe_attachment_filename(download_filename)}"'
    )
    return cast(
        str,
        s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.s3_bucket,
                "Key": s3_key,
                "ResponseContentDisposition": disposition,
            },
            ExpiresIn=expires_in,
        ),
    )
