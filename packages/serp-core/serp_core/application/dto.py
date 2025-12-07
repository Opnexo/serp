"""
Base DTO (Data Transfer Object) class
"""

from abc import ABC

from pydantic import BaseModel


class DTO(BaseModel, ABC):
    """
    Base class for Data Transfer Objects.

    DTOs:
    - Transfer data between layers
    - Use Pydantic for validation
    - Are serializable to JSON
    - Don't contain business logic

    Example:
        class CustomerDTO(DTO):
            id: UUID
            name: str
            email: str
            created_at: datetime

            @classmethod
            def from_entity(cls, customer: Customer) -> 'CustomerDTO':
                return cls(
                    id=customer.id,
                    name=customer.name,
                    email=customer.email,
                    created_at=customer.created_at
                )

        class RegisterCustomerDTO(DTO):
            name: str
            email: EmailStr

            @field_validator('name')
            def name_must_not_be_empty(cls, v: str) -> str:
                if not v.strip():
                    raise ValueError('Name cannot be empty')
                return v
    """

    class Config:
        from_attributes = True  # Allow creating from ORM models
        json_encoders = {
            # Add custom encoders if needed
        }
