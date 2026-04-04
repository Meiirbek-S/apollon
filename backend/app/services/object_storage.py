from minio import Minio
from minio.error import S3Error

from app.core.config import settings


def get_minio_client() -> Minio:
    endpoint = f"{settings.minio_host}:{settings.minio_port}"
    return Minio(endpoint, access_key=settings.minio_root_user, secret_key=settings.minio_root_password, secure=False)


def ensure_bucket_exists(client: Minio) -> None:
    found = client.bucket_exists(settings.minio_bucket)
    if not found:
        client.make_bucket(settings.minio_bucket)


def upload_file(client: Minio, object_name: str, file_path: str, content_type: str) -> None:
    try:
        client.fput_object(settings.minio_bucket, object_name, file_path, content_type=content_type)
    except S3Error as exc:
        raise RuntimeError(f"failed to upload to minio: {exc}") from exc
