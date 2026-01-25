"""
Generic project type entities.

For engineering teams working on IIoT, Telecom, hardware/software solutions.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Optional
from uuid import UUID

from serp_core.domain.entity import Entity


@dataclass
class Phase(Entity):
    """
    Project phase for sequential/waterfall-style workflows.
    
    Common phases: Design, Development, Testing, Deployment
    """

    project_id: UUID
    name: str
    description: str = ""
    order: int = 0  # Display order
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Deliverable(Entity):
    """
    Trackable deliverable/output for a project.
    
    Examples: Design Document, Prototype, Test Report, Final Product
    """

    project_id: UUID
    phase_id: Optional[UUID] = None  # Optional link to phase
    name: str
    description: str = ""
    due_date: Optional[date] = None
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, DELIVERED
    responsible_id: Optional[UUID] = None  # Person responsible
    metadata: dict[str, Any] = field(default_factory=dict)
