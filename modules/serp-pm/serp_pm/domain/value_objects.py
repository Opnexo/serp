"""
Value objects for Project Management module.
"""

from dataclasses import dataclass
from enum import Enum

from serp_core.domain.value_object import ValueObject


class ProjectStatus(str, Enum):
    """Project status enumeration."""

    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TaskStatus(str, Enum):
    """Task status enumeration."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CLOSED = "CLOSED"


class Priority(str, Enum):
    """Priority level enumeration."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class TimeEstimate(ValueObject):
    """
    Time estimate value object.

    Can represent hours, story points, or other units depending on methodology.
    """

    value: float
    unit: str = "hours"  # hours, story_points, days

    def __post_init__(self) -> None:
        """Validate time estimate."""
        if self.value < 0:
            raise ValueError("Time estimate cannot be negative")
        if self.unit not in ("hours", "story_points", "days"):
            raise ValueError(f"Invalid unit: {self.unit}")

    def to_hours(self) -> float:
        """
        Convert to hours (rough estimate).

        For story points, assumes 1 point = 8 hours.
        For days, assumes 1 day = 8 hours.
        """
        if self.unit == "hours":
            return self.value
        elif self.unit == "story_points":
            return self.value * 8
        elif self.unit == "days":
            return self.value * 8
        return self.value
