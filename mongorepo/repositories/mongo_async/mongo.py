from typing import List, Optional

from bson import ObjectId

from mongorepo.repositories.base import AbstractRepository, T


class AsyncRepository(AbstractRepository[T]):
    def __init__(self, database):
        super().__init__(database)

    async def list_all(self, query: Optional[dict] = None) -> List[T]:
        collection = self.get_collection()

        if query is None:
            query = {}

        async_cursor = collection.find(query, projection=self.get_projection())

        return [
            self._model_class(**document) async for document in async_cursor
        ]  # noqa: E501

    async def find_by_query(self, query: dict) -> Optional[T]:
        collection = self.get_collection()
        if document := await collection.find_one(
            query, projection=self.get_projection()
        ):
            return self._model_class(**document)
        return None

    async def find_by_id(self, document_id: str) -> Optional[T]:
        collection = self.get_collection()
        document = await collection.find_one(
            {"_id": ObjectId(document_id)},
            projection=self.get_projection(),
        )
        return self._model_class(**document)

    async def save(self, model: T):
        collection = self.get_collection()
        raw_model = model.dict(by_alias=True, exclude_none=True)

        if id_model := raw_model.get("_id", raw_model.get("id")):
            await collection.update_one(
                {"_id": ObjectId(id_model)}, {"$set": raw_model}
            )  # noqa: E501
            return await self.find_by_id(model.id)

        document = await collection.insert_one(raw_model)

        return await self.find_by_id(str(document.inserted_id))

    async def delete(self, model: T) -> bool:
        collection = self.get_collection()
        raw_model = model.dict(by_alias=True, exclude_none=True)
        if model_id := raw_model.get("_id", raw_model.get("id")):
            await collection.delete_one({"_id": ObjectId(model_id)})
            return True
        return False
