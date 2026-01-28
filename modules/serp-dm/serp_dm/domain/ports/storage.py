"""
Storage port interface for document file storage.

This interface defines the contract for S3-compatible storage backends.
Implementations include MinIO, Garage, AWS S3, etc.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class StorageObject:
    """Metadata about a stored object."""

    key: str
    size_bytes: int
    content_type: str
    etag: str  # MD5 hash
    last_modified: str


@dataclass
class PresignedUrl:
    """Presigned URL for direct browser access."""

    url: str
    expires_at: str
    method: str = "GET"  # GET for download, PUT for upload


class IDocumentStorage(ABC):
    """
    Generic interface for document file storage.

    Implementations:
    - MinioStorageAdapter (default)
    - GarageStorageAdapter
    - S3StorageAdapter
    - LocalFileSystemAdapter (for testing)
    """

    @abstractmethod
    async def upload(
        self,
        key: str,
        content: bytes,
        content_type: str,
        metadata: Optional[dict[str, str]] = None,
    ) -> StorageObject:
        """
        Upload a file to storage.

        Args:
            key: Storage key (path) for the file
            content: File content as bytes
            content_type: MIME type of the file
            metadata: Optional custom metadata

        Returns:
            StorageObject with upload result
        """
        ...

    @abstractmethod
    async def download(self, key: str) -> bytes:
        """
        Download a file from storage.

        Args:
            key: Storage key (path) of the file

        Returns:
            File content as bytes

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """
        Delete a file from storage.

        Args:
            key: Storage key (path) of the file
        """
        ...

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            key: Storage key (path) of the file

        Returns:
            True if file exists, False otherwise
        """
        ...

    @abstractmethod
    async def get_metadata(self, key: str) -> StorageObject:
        """
        Get metadata for a file without downloading it.

        Args:
            key: Storage key (path) of the file

        Returns:
            StorageObject with file metadata

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        ...

    @abstractmethod
    async def get_presigned_download_url(
        self,
        key: str,
        expires_in_seconds: int = 3600,
        filename: Optional[str] = None,
    ) -> PresignedUrl:
        """
        Generate a presigned URL for direct browser download.

        Args:
            key: Storage key (path) of the file
            expires_in_seconds: URL expiration time (default 1 hour)
            filename: Optional filename for Content-Disposition header

        Returns:
            PresignedUrl with download URL
        """
        ...

    @abstractmethod
    async def get_presigned_upload_url(
        self,
        key: str,
        content_type: str,
        expires_in_seconds: int = 3600,
    ) -> PresignedUrl:
        """
        Generate a presigned URL for direct browser upload.

        Args:
            key: Storage key (path) for the upload
            content_type: Expected MIME type of the upload
            expires_in_seconds: URL expiration time (default 1 hour)

        Returns:
            PresignedUrl with upload URL
        """
        ...

    @abstractmethod
    async def list_objects(
        self,
        prefix: str,
        max_keys: int = 1000,
    ) -> list[StorageObject]:
        """
        List objects with a given prefix.

        Args:
            prefix: Key prefix to filter by
            max_keys: Maximum number of objects to return

        Returns:
            List of StorageObject matching the prefix
        """
        ...

    @abstractmethod
    async def copy(
        self,
        source_key: str,
        destination_key: str,
    ) -> StorageObject:
        """
        Copy an object within storage.

        Args:
            source_key: Source storage key
            destination_key: Destination storage key

        Returns:
            StorageObject for the copied file
        """
        ...
