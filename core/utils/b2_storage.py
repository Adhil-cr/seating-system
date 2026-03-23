import os
from datetime import datetime

import boto3
from botocore.exceptions import BotoCoreError, ClientError


B2_ENABLED = os.getenv("B2_STORAGE_ENABLED", "false").lower() == "true"
B2_BUCKET = os.getenv("B2_BUCKET", "")
B2_KEY_ID = os.getenv("B2_KEY_ID", "")
B2_APP_KEY = os.getenv("B2_APP_KEY", "")
B2_ENDPOINT = os.getenv("B2_ENDPOINT", "")
B2_REGION = os.getenv("B2_REGION", "")
B2_PREFIX = os.getenv("B2_PREFIX", "")
B2_STRICT = os.getenv("B2_STRICT", "false").lower() == "true"


_client = None


def b2_enabled():
    return B2_ENABLED and B2_BUCKET and B2_KEY_ID and B2_APP_KEY and B2_ENDPOINT


def _get_client():
    global _client
    if _client is not None:
        return _client
    _client = boto3.client(
        "s3",
        endpoint_url=B2_ENDPOINT,
        region_name=B2_REGION or None,
        aws_access_key_id=B2_KEY_ID or None,
        aws_secret_access_key=B2_APP_KEY or None,
    )
    return _client


def _apply_prefix(key: str) -> str:
    if B2_PREFIX:
        return f"{B2_PREFIX.strip('/')}/{key.lstrip('/')}"
    return key


def upload_file(local_path: str, key: str, content_type: str | None = None):
    if not b2_enabled():
        return False

    key = _apply_prefix(key)
    extra = {}
    if content_type:
        extra["ContentType"] = content_type

    try:
        client = _get_client()
        if extra:
            client.upload_file(local_path, B2_BUCKET, key, ExtraArgs=extra)
        else:
            client.upload_file(local_path, B2_BUCKET, key)
        return True
    except (BotoCoreError, ClientError) as exc:
        if B2_STRICT:
            raise
        print(f"B2 upload failed for {local_path}: {exc}")
        return False


def build_prefix(*parts: str) -> str:
    safe = [p.strip("/") for p in parts if p]
    return "/".join(safe)


def timestamp_prefix() -> str:
    return datetime.utcnow().strftime("%Y%m%d-%H%M%S")


def upload_bytes(data: bytes, key: str, content_type: str | None = None):
    if not b2_enabled():
        return False

    key = _apply_prefix(key)
    extra = {"Body": data}
    if content_type:
        extra["ContentType"] = content_type

    try:
        client = _get_client()
        client.put_object(Bucket=B2_BUCKET, Key=key, **extra)
        return True
    except (BotoCoreError, ClientError) as exc:
        if B2_STRICT:
            raise
        print(f"B2 upload failed for {key}: {exc}")
        return False


def upload_fileobj(fileobj, key: str, content_type: str | None = None):
    if not b2_enabled():
        return False

    key = _apply_prefix(key)
    extra = {}
    if content_type:
        extra["ContentType"] = content_type

    try:
        client = _get_client()
        if extra:
            client.upload_fileobj(fileobj, B2_BUCKET, key, ExtraArgs=extra)
        else:
            client.upload_fileobj(fileobj, B2_BUCKET, key)
        return True
    except (BotoCoreError, ClientError) as exc:
        if B2_STRICT:
            raise
        print(f"B2 upload failed for {key}: {exc}")
        return False
