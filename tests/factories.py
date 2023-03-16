from pydantic import BaseModel
from pydantic_factories import ModelFactory


class Data(BaseModel):
    name: str
    age: int
    job: str


class DataFactory(ModelFactory):
    __model__ = Data
