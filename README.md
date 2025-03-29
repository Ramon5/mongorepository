# Mongo Repository

This package provide a sync and async repositories utilities for mongodb.

## Tutorial
=======

The first step is to create a schema inheriting from MongoBaseModel and then create a specialized repository inheriting from Repository or AsyncRepository according to the application.

Creating a db schema

```
from mongorepository.models import MongoBaseModel

class Person(MongoBaseModel):
    name: str
    age: int
    job: Optional[str]

```

Then create a person repository inheriting from Repository

```
import pymongo
from mongorepository.repositories.mongo import Repository

def get_database(db_name: str):
    client = pymongo.MongoClient("mongodb://localhost:2707")
    return client.get_database(db_name)

class PersonRepository(Repository[Person]):
    def __init__(self):
        super().__init__(get_database("my_db_name"))

    class Config:
        collection = "persons"

```

And then:

```

person = Person(name="John Doe", age=33)
repository = PersonRepository()

repository.save(person)

```

For async flow use this:

```
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from mongorepository.repositories.async_mongo import AsyncRepository


def get_database(db_name):
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    database = client.get_database(db_name)
    database.get_io_loop = asyncio.get_event_loop
    return database


class PersonRepository(AsyncRepository[Person]):

    def __init__(self):
        super().__init__(get_database("my_db_name"))

    class Config:
        collection = "persons"


person = Person(name="John Doe", age=33)
repository = PersonRepository()

asyncio.run(repository.save(person))
```

