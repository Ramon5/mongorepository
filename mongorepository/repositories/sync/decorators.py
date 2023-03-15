from functools import wraps
from typing import Callable

from pymongo import MongoClient


def atomic_transaction(db_client: MongoClient):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with db_client.start_session() as session:
                with session.start_transaction():
                    return func(*args, **kwargs)

        return wrapper

    return decorator
