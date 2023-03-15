from functools import wraps
from typing import Callable

from pymongo import MongoClient


def atomic_transaction(db_client: MongoClient):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with await db_client.start_session() as session:
                async with session.start_transaction():
                    return await func(*args, **kwargs)

        return wrapper

    return decorator
