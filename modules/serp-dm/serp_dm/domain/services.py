"""
Domain services for Document Management module.
"""

from typing import Optional
from uuid import UUID

from serp_dm.domain.entities import Document, Folder


class DocumentDomainService:
    """
    Domain service for document business logic.
    """

    @staticmethod
    def can_move_to_folder(document: Document, target_folder_id: Optional[UUID]) -> bool:
        """
        Check if document can be moved to target folder.

        Args:
            document: Document to move
            target_folder_id: Target folder ID

        Returns:
            True if move is allowed
        """
        # Add business rules here
        # For example: check permissions, folder limits, etc.
        return True

    @staticmethod
    def calculate_storage_size(documents: list[Document]) -> int:
        """
        Calculate total storage size for documents.

        Args:
            documents: List of documents

        Returns:
            Total size in bytes
        """
        return sum(doc.size_bytes for doc in documents)


class FolderDomainService:
    """
    Domain service for folder business logic.
    """

    @staticmethod
    def can_delete_folder(folder: Folder, has_children: bool, has_documents: bool) -> bool:
        """
        Check if folder can be deleted.

        Args:
            folder: Folder to delete
            has_children: Whether folder has child folders
            has_documents: Whether folder has documents

        Returns:
            True if deletion is allowed
        """
        # Business rule: Only delete empty folders
        return not has_children and not has_documents

    @staticmethod
    def build_path(parent_path: str, folder_name: str) -> str:
        """
        Build full path for a folder.

        Args:
            parent_path: Parent folder path
            folder_name: Folder name

        Returns:
            Full folder path
        """
        if parent_path == "/":
            return f"/{folder_name}"
        return f"{parent_path}/{folder_name}"

    @staticmethod
    def calculate_depth(path: str) -> int:
        """
        Calculate folder depth from root.

        Args:
            path: Folder path

        Returns:
            Depth level (0 for root)
        """
        if path == "/":
            return 0
        return len([p for p in path.split("/") if p])
