"""
Base ApplicationService class
"""

from abc import ABC


class ApplicationService(ABC):
    """
    Base class for application services.

    Application services:
    - Orchestrate domain operations
    - Handle transactions (via UnitOfWork)
    - Transform between DTOs and domain objects
    - Coordinate multiple repositories and domain services
    - Don't contain business logic (that belongs in domain)

    Example:
        class CustomerApplicationService(ApplicationService):
            def __init__(
                self,
                customer_repository: CustomerRepository,
                uow: UnitOfWork
            ):
                self.customer_repository = customer_repository
                self.uow = uow

            async def register_customer(
                self,
                dto: RegisterCustomerDTO
            ) -> CustomerDTO:
                async with self.uow:
                    # Domain logic
                    customer = Customer.create(
                        name=dto.name,
                        email=dto.email
                    )

                    # Persistence
                    await self.customer_repository.save(customer)

                    # Commit transaction
                    await self.uow.commit()

                    # Return DTO
                    return CustomerDTO.from_entity(customer)
    """

    pass
