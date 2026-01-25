"""
Basic tests for Document Management module.
"""

import pytest
from uuid import uuid4

from serp_dm.domain.entities import Document, Folder
from serp_dm.domain.value_objects import FileMetadata, FilePath, DocumentTag


def test_document_creation():
    """Test document entity creation."""
    doc = Document(
        id=uuid4(),
        name="test.pdf",
        folder_id=None,
        file_path="/uploads/test.pdf",
        mime_type="application/pdf",
        size_bytes=1024,
        checksum="abc123",
    )
    assert doc.name == "test.pdf"
    assert doc.version == 1
    assert not doc.is_archived


def test_document_archive():
    """Test document archiving."""
    doc = Document(
        id=uuid4(),
        name="test.pdf",
        folder_id=None,
        file_path="/uploads/test.pdf",
        mime_type="application/pdf",
        size_bytes=1024,
        checksum="abc123",
    )
    doc.archive()
    assert doc.is_archived

    doc.restore()
    assert not doc.is_archived


def test_folder_creation():
    """Test folder entity creation."""
    folder = Folder(
        id=uuid4(),
        name="Documents",
        parent_id=None,
        path="/Documents",
    )
    assert folder.name == "Documents"
    assert folder.path == "/Documents"
    assert not folder.is_archived


def test_file_metadata_value_object():
    """Test FileMetadata value object."""
    metadata = FileMetadata(
        file_name="test.pdf",
        mime_type="application/pdf",
        size_bytes=1024,
        checksum="abc123",
        extension="pdf",
    )
    assert metadata.file_name == "test.pdf"
    assert metadata.size_bytes == 1024


def test_file_path_value_object():
    """Test FilePath value object."""
    path = FilePath(path="/uploads/test.pdf")
    assert path.directory == "/uploads"
    assert path.filename == "test.pdf"


def test_document_tag_validation():
    """Test DocumentTag validation."""
    tag = DocumentTag(name="important")
    assert tag.name == "important"

    with pytest.raises(ValueError):
        DocumentTag(name="")

    with pytest.raises(ValueError):
        DocumentTag(name="a" * 51)
