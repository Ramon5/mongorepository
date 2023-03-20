from typing import Optional

import mongomock
import mongomock_motor
import pytest

from mongorepository.models import MongoBaseModel
from mongorepository.repositories.async_mongo import AsyncRepository
from mongorepository.repositories.mongo import Repository


class AsyncMongoClient(mongomock_motor.AsyncMongoMockClient):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


@pytest.fixture
def database():
    with mongomock.MongoClient("mongodb://localhost:27017") as client:
        db = client["db_test"]
        yield db


@pytest.fixture
def model_class():
    class Data(MongoBaseModel):
        name: str
        age: int
        job: Optional[str]

    return Data


@pytest.fixture
def repository(database, model_class):
    class DataRepository(Repository[model_class]):
        def __init__(self):
            super().__init__(database)

        class Config:
            collection = "data"

    return DataRepository()


@pytest.fixture
def async_database():
    with AsyncMongoClient("mongodb://localhost:27017") as client:
        db = client["db_test"]
        yield db


@pytest.fixture
def async_repository(async_database, model_class):
    class DataRepository(AsyncRepository[model_class]):
        def __init__(self):
            super().__init__(async_database)

        class Config:
            collection = "data"

    return DataRepository()
