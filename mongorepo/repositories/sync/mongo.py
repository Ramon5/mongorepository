from typing import List, Optional

from bson import ObjectId

from mongorepo.repositories.base import AbstractRepository, T


class Repository(AbstractRepository[T]):
    def __init__(self, database):
        super().__init__(database)

    def list_all(self, query: Optional[dict] = None) -> List[T]:
        collection = self.get_collection()
        if query is None:
            query = {}

        cursor = collection.find(query)

        return [self._model_class(**document) for document in cursor]

    def find_by_query(self, query: dict) -> Optional[T]:
        collection = self.get_collection()
        if document := collection.find_one(query):
            return self._model_class(**document)
        return None

    def find_by_id(self, document_id: str) -> Optional[T]:
        collection = self.get_collection()
        document = collection.find_one(
            {"_id": ObjectId(document_id)},
            projection=self.get_projection(),
        )
        return self._model_class(**document)

    def save(self, model: T) -> T:
        collection = self.get_collection()
        raw_model = model.dict(by_alias=True, exclude_none=True)

        if id_model := raw_model.get("_id", raw_model.get("id")):
            collection.update_one(
                {"_id": ObjectId(id_model)}, {"$set": raw_model}
            )  # noqa: E501
            return self.find_by_id(model.id)

        document = collection.insert_one(raw_model)

        return self.find_by_id(str(document.inserted_id))

    def delete(self, model: T) -> bool:
        collection = self.get_collection()
        raw_model = model.dict(by_alias=True, exclude_none=True)
        if id_model := raw_model.get("_id", raw_model.get("id")):
            collection.delete_one({"_id": ObjectId(id_model)})
            return True
        return False
