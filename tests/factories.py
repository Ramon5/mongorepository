from pydantic import BaseModel
from polyfactory.factories.pydantic_factory import ModelFactory


class Data(BaseModel):
    name: str
    age: int
    job: str


class DataFactory(ModelFactory):
    __model__ = Data