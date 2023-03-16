from typing import List, Optional

import pymongo
from bson import ObjectId

from mongorepository.repositories.base import AbstractRepository, T


class AsyncRepository(AbstractRepository[T]):
    def __init__(self, database):
        super().__init__(database)

    async def __get_paginated_documents(self, query, sort, next_key=None):
        collection = self.get_collection()
        query, next_key_fn = self.generate_pagination_query(
            query, sort, next_key
        )  # noqa: E501

        async_cursor = (
            collection.find(query, projection=self.get_projection())
            .sort(sort)
            .limit(self._query_limit)
        )

        documents = [document async for document in async_cursor]  # noqa: E501

        return {
            "total": len(documents),
            "results": documents,
            "next_page": next_key_fn(documents),
        }

    async def list_all(
        self,
        query: Optional[dict] = None,
        sort: Optional[List] = None,
        next_page: Optional[dict] = None,
    ) -> List[T]:
        collection = self.get_collection()

        if query is None:
            query = {}

        if not sort:
            sort = [("_id", pymongo.DESCENDING)]

        if self._paginated:
            result = await self.__get_paginated_documents(
                query, sort, next_page
            )  # noqa: E501
            self._convert_paginated_results_to_model(result)
            return result

        async_cursor = collection.find(
            query, projection=self.get_projection()
        ).sort(  # noqa: E501
            sort
        )

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

    async def bulk_create(self, models: List[T]) -> List[ObjectId]:
        raw_models = [model.dict(exclude_none=True) for model in models]
        result = await self.get_collection().insert_many(raw_models)
        return result.inserted_ids

    async def delete(self, model: T) -> bool:
        collection = self.get_collection()
        raw_model = model.dict(by_alias=True, exclude_none=True)
        if model_id := raw_model.get("_id", raw_model.get("id")):
            await collection.delete_one({"_id": ObjectId(model_id)})
            return True
        return False
