"""
Domain layer exceptions
"""


class DomainError(Exception):
    """Base exception for domain errors"""

    pass


class EntityNotFoundError(DomainError):
    """Raised when an entity is not found"""

    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with id {entity_id} not found")


class InvalidOperationError(DomainError):
    """Raised when a domain operation is invalid"""

    pass


class BusinessRuleViolationError(DomainError):
    """Raised when a business rule is violated"""

    pass
