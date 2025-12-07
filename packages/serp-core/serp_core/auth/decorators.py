"""
Decorator utilities for common patterns
"""

from functools import wraps
from typing import Callable


def transactional(func: Callable) -> Callable:
    """
    Decorator to wrap a function in a transaction.

    The function must accept a 'uow' parameter (Unit of Work).

    Example:
        @transactional
        async def transfer_funds(
            from_account: Account,
            to_account: Account,
            amount: Money,
            uow: UnitOfWork
        ):
            from_account.withdraw(amount)
            to_account.deposit(amount)
            await account_repo.save(from_account)
            await account_repo.save(to_account)
            # Transaction is automatically committed
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        uow = kwargs.get("uow")
        if uow is None:
            raise ValueError("Function must receive 'uow' parameter")

        async with uow:
            result = await func(*args, **kwargs)
            await uow.commit()
            return result

    return wrapper
