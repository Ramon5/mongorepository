from functools import wraps
from typing import Callable

from motor.motor_asyncio import AsyncIOMotorClient


def atomic_transaction(db_client: AsyncIOMotorClient):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with await db_client.start_session() as session:
                async with session.start_transaction():
                    return await func(*args, **kwargs)

        return wrapper

    return decorator
