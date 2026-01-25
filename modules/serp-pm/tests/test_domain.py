"""Basic tests for PM domain."""

import pytest
from uuid import uuid4

from serp_pm.domain.entities import Project, Task


def test_project_creation():
    """Test project entity creation."""
    project = Project(id=uuid4(), name="Test Project", description="Test description")
    assert project.name == "Test Project"
    assert project.status == "PLANNING"
    assert not project.is_archived


def test_project_start():
    """Test starting a project."""
    project = Project(id=uuid4(), name="Test Project")
    project.start()
    assert project.status == "ACTIVE"


def test_task_creation():
    """Test task entity creation."""
    task = Task(id=uuid4(), project_id=uuid4(), title="Test Task")
    assert task.title == "Test Task"
    assert task.status == "OPEN"
    assert task.priority == "MEDIUM"


def test_task_assign():
    """Test assigning a task."""
    task = Task(id=uuid4(), project_id=uuid4(), title="Test Task")
    user_id = uuid4()
    task.assign(user_id)
    assert task.assigned_to == user_id
