"""
Base DomainService class for Domain-Driven Design
"""

from abc import ABC


class DomainService(ABC):
    """
    Base class for domain services.

    Domain services:
    - Contain domain logic that doesn't belong to a single entity
    - Are stateless
    - Operate on domain objects
    - Use domain language

    Use domain services when:
    - An operation involves multiple aggregates
    - The logic doesn't naturally fit in any entity
    - You need to coordinate between entities

    Example:
        class TransferService(DomainService):
            async def transfer_funds(
                self,
                from_account: Account,
                to_account: Account,
                amount: Money
            ) -> None:
                if from_account.balance < amount:
                    raise InsufficientFundsError()

                from_account.withdraw(amount)
                to_account.deposit(amount)

        class PricingService(DomainService):
            def calculate_price(
                self,
                product: Product,
                customer: Customer,
                quantity: int
            ) -> Money:
                base_price = product.price
                discount = customer.get_discount_rate()
                volume_discount = self._calculate_volume_discount(quantity)

                return base_price * quantity * (1 - discount) * (1 - volume_discount)
    """

    pass
