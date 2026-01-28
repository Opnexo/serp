"""
MinIO storage adapter implementing IDocumentStorage.

MinIO is an S3-compatible object storage server.
This adapter uses the minio Python SDK for async operations.
"""

import asyncio
from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional
from urllib.parse import urlencode

from minio import Minio
from minio.error import S3Error

from serp_dm.domain.ports.storage import (
    IDocumentStorage,
    PresignedUrl,
    StorageObject,
)


class MinioStorageAdapter(IDocumentStorage):
    """
    MinIO implementation of document storage.

    Configuration via environment variables:
    - SERP_DM_MINIO_ENDPOINT: MinIO server endpoint (default: localhost:9000)
    - SERP_DM_MINIO_ACCESS_KEY: Access key (default: minioadmin)
    - SERP_DM_MINIO_SECRET_KEY: Secret key (default: minioadmin)
    - SERP_DM_MINIO_BUCKET: Bucket name (default: serp-documents)
    - SERP_DM_MINIO_SECURE: Use HTTPS (default: false)
    """

    def __init__(
        self,
        endpoint: str = "localhost:9000",
        access_key: str = "minioadmin",
        secret_key: str = "minioadmin",
        bucket: str = "serp-documents",
        secure: bool = False,
    ):
        """
        Initialize MinIO client.

        Args:
            endpoint: MinIO server endpoint (host:port)
            access_key: MinIO access key
            secret_key: MinIO secret key
            bucket: Default bucket name
            secure: Use HTTPS (True) or HTTP (False)
        """
        self._client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self._bucket = bucket
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Create bucket if it doesn't exist."""
        try:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
        except S3Error as e:
            # Log error but don't fail - bucket might be created by admin
            pass

    def _run_sync(self, coro):
        """Helper to run sync operations (MinIO SDK is synchronous)."""
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in an async context, run in thread pool
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return loop.run_in_executor(pool, lambda: coro)
        return coro

    async def upload(
        self,
        key: str,
        content: bytes,
        content_type: str,
        metadata: Optional[dict[str, str]] = None,
    ) -> StorageObject:
        """Upload a file to MinIO."""
        data = BytesIO(content)
        size = len(content)

        # MinIO SDK is synchronous, wrap in executor
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self._client.put_object(
                bucket_name=self._bucket,
                object_name=key,
                data=data,
                length=size,
                content_type=content_type,
                metadata=metadata or {},
            ),
        )

        return StorageObject(
            key=key,
            size_bytes=size,
            content_type=content_type,
            etag=result.etag.strip('"'),
            last_modified=datetime.utcnow().isoformat(),
        )

    async def download(self, key: str) -> bytes:
        """Download a file from MinIO."""
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                lambda: self._client.get_object(
                    bucket_name=self._bucket,
                    object_name=key,
                ),
            )
            content = response.read()
            response.close()
            response.release_conn()
            return content
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise FileNotFoundError(f"File not found: {key}")
            raise

    async def delete(self, key: str) -> None:
        """Delete a file from MinIO."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self._client.remove_object(
                bucket_name=self._bucket,
                object_name=key,
            ),
        )

    async def exists(self, key: str) -> bool:
        """Check if a file exists in MinIO."""
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                lambda: self._client.stat_object(
                    bucket_name=self._bucket,
                    object_name=key,
                ),
            )
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            raise

    async def get_metadata(self, key: str) -> StorageObject:
        """Get metadata for a file without downloading it."""
        loop = asyncio.get_event_loop()
        try:
            stat = await loop.run_in_executor(
                None,
                lambda: self._client.stat_object(
                    bucket_name=self._bucket,
                    object_name=key,
                ),
            )
            return StorageObject(
                key=key,
                size_bytes=stat.size,
                content_type=stat.content_type or "application/octet-stream",
                etag=stat.etag.strip('"'),
                last_modified=stat.last_modified.isoformat() if stat.last_modified else "",
            )
        except S3Error as e:
            if e.code == "NoSuchKey":
                raise FileNotFoundError(f"File not found: {key}")
            raise

    async def get_presigned_download_url(
        self,
        key: str,
        expires_in_seconds: int = 3600,
        filename: Optional[str] = None,
    ) -> PresignedUrl:
        """Generate a presigned URL for direct browser download."""
        loop = asyncio.get_event_loop()

        # Build response headers for Content-Disposition
        response_headers = {}
        if filename:
            # URL encode the filename for Content-Disposition
            response_headers["response-content-disposition"] = f'attachment; filename="{filename}"'

        url = await loop.run_in_executor(
            None,
            lambda: self._client.presigned_get_object(
                bucket_name=self._bucket,
                object_name=key,
                expires=timedelta(seconds=expires_in_seconds),
                response_headers=response_headers if response_headers else None,
            ),
        )

        expires_at = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
        return PresignedUrl(
            url=url,
            expires_at=expires_at.isoformat(),
            method="GET",
        )

    async def get_presigned_upload_url(
        self,
        key: str,
        content_type: str,
        expires_in_seconds: int = 3600,
    ) -> PresignedUrl:
        """Generate a presigned URL for direct browser upload."""
        loop = asyncio.get_event_loop()

        url = await loop.run_in_executor(
            None,
            lambda: self._client.presigned_put_object(
                bucket_name=self._bucket,
                object_name=key,
                expires=timedelta(seconds=expires_in_seconds),
            ),
        )

        expires_at = datetime.utcnow() + timedelta(seconds=expires_in_seconds)
        return PresignedUrl(
            url=url,
            expires_at=expires_at.isoformat(),
            method="PUT",
        )

    async def list_objects(
        self,
        prefix: str,
        max_keys: int = 1000,
    ) -> list[StorageObject]:
        """List objects with a given prefix."""
        loop = asyncio.get_event_loop()

        objects = await loop.run_in_executor(
            None,
            lambda: list(
                self._client.list_objects(
                    bucket_name=self._bucket,
                    prefix=prefix,
                    recursive=True,
                )
            )[:max_keys],
        )

        return [
            StorageObject(
                key=obj.object_name,
                size_bytes=obj.size or 0,
                content_type="application/octet-stream",  # Not available in list
                etag=obj.etag.strip('"') if obj.etag else "",
                last_modified=obj.last_modified.isoformat() if obj.last_modified else "",
            )
            for obj in objects
        ]

    async def copy(
        self,
        source_key: str,
        destination_key: str,
    ) -> StorageObject:
        """Copy an object within storage."""
        from minio.commonconfig import CopySource

        loop = asyncio.get_event_loop()

        result = await loop.run_in_executor(
            None,
            lambda: self._client.copy_object(
                bucket_name=self._bucket,
                object_name=destination_key,
                source=CopySource(self._bucket, source_key),
            ),
        )

        # Get metadata of copied object
        return await self.get_metadata(destination_key)
