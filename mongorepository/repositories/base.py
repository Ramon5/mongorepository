from typing import Generic, TypeVar

from mongorepository.models.mongo import MongoBaseModel

T = TypeVar("T", bound=MongoBaseModel)


class AbstractRepository(Generic[T]):
    def __init__(self, database):
        self.__database = database
        self.__collection_name = self.Config.collection
        self._model_class = self.__orig_bases__[0].__args__[0]

    def get_collection(self):
        return self.__database.get_collection(self.__collection_name)

    def get_projection(self) -> dict:
        projection = self._model_class.projection()
        if hasattr(self.Config, "projection"):
            projection = self.Config.projection
        return projection
