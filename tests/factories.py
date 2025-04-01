from dataclasses import dataclass

import factory


@dataclass
class Data:
    name: str
    age: int
    job: str


class DataFactory(factory.Factory):
    class Meta:
        model = Data

    name = factory.Faker("name")
    age = factory.Faker("random_int", min=18, max=65)
    job = factory.Faker("job")
