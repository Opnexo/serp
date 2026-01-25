"""Tests for project type registry."""

import pytest

from serp_pm.types.interface import IProjectType
from serp_pm.types.registry import ProjectTypeRegistry


def test_registry_discovers_built_in_types():
    """Test that registry discovers the three built-in types."""
    # Reset registry
    ProjectTypeRegistry.reset()
    
    # Discover types
    ProjectTypeRegistry.discover()
    
    # Should have 3 types
    all_types = ProjectTypeRegistry.all_types()
    assert len(all_types) >= 3  # At least generic, kanban, scrum
    
    type_ids = ProjectTypeRegistry.get_type_ids()
    assert "generic" in type_ids
    assert "kanban" in type_ids
    assert "scrum" in type_ids


def test_registry_get_type():
    """Test getting a specific project type."""
    ProjectTypeRegistry.reset()
    ProjectTypeRegistry.discover()
    
    generic = ProjectTypeRegistry.get("generic")
    assert generic is not None
    assert generic.type_id == "generic"
    assert generic.display_name == "Generic Project"


def test_registry_is_valid_type():
    """Test type validation."""
    ProjectTypeRegistry.reset()
    ProjectTypeRegistry.discover()
    
    assert ProjectTypeRegistry.is_valid_type("generic")
    assert ProjectTypeRegistry.is_valid_type("kanban")
    assert ProjectTypeRegistry.is_valid_type("scrum")
    assert not ProjectTypeRegistry.is_valid_type("invalid")


def test_generic_project_type():
    """Test generic project type."""
    ProjectTypeRegistry.reset()
    ProjectTypeRegistry.discover()
    
    generic = ProjectTypeRegistry.get("generic")
    assert generic.type_id == "generic"
    assert "engineering" in generic.description.lower() or "iot" in generic.description.lower()
    
    ui_config = generic.get_ui_config()
    assert "views" in ui_config
    assert "toolbar" in ui_config


def test_kanban_project_type():
    """Test kanban project type."""
    ProjectTypeRegistry.reset()
    ProjectTypeRegistry.discover()
    
    kanban = ProjectTypeRegistry.get("kanban")
    assert kanban.type_id == "kanban"
    assert "board" in kanban.description.lower()
    
    ui_config = kanban.get_ui_config()
    assert "views" in ui_config


def test_scrum_project_type():
    """Test scrum project type."""
    ProjectTypeRegistry.reset()
    ProjectTypeRegistry.discover()
    
    scrum = ProjectTypeRegistry.get("scrum")
    assert scrum.type_id == "scrum"
    assert "sprint" in scrum.description.lower()
    
    ui_config = scrum.get_ui_config()
    assert "views" in ui_config
