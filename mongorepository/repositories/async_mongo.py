from typing import Any, Dict, List, Optional, Tuple, Union

import pymongo
from bson import ObjectId
from motor.core import Cursor
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import DeleteResult, InsertManyResult, InsertOneResult

from mongorepository.repositories.base import AbstractRepository, T

class AsyncRepository(AbstractRepository[T]):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database)

    async def __get_paginated_documents(
        self,
        query: Dict[str, Any],
        sort: List[Tuple[str, int]],
        next_key: Optional[Dict[str, Any]],
        projection: Dict[str, Any],
    ) -> Dict[str, Any]:
        collection = self.get_collection()
        query, next_key_fn = self.generate_pagination_query(
            query, sort, next_key
        )  # noqa: E501

        cursor: Cursor = (
            collection.find(query, projection=projection)
            .sort(sort)
            .limit(self._query_limit)
        )

        documents = [document async for document in cursor]  # noqa: E501

        return {
            "total": len(documents),
            "results": documents,
            "next_page": next_key_fn(documents),
        }

    async def list_objects(
        self,
        query: Optional[Dict[str, Any]] = None,
        sort: Optional[List[Tuple[str, int]]] = None,
        next_page: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, Any]] = None,
    ) -> Union[List[T], Dict[str, Any]]:
        collection = self.get_collection()

        if query is None:
            query = {}

        if not sort:
            sort = [("_id", pymongo.DESCENDING)]

        if self._paginated:
            result = await self.__get_paginated_documents(
                query, sort, next_page, projection or self.get_projection()
            )  # noqa: E501
            self._convert_paginated_results_to_model(result)
            return result

        cursor: Cursor = collection.find(
            query, projection=projection or self.get_projection()
        ).sort(  # noqa: E501
            sort
        )

        return [
            self._model_class(**document) async for document in cursor
        ]  # noqa: E501

    async def list_distinct(
        self,
        field: str,
        query: Dict[str, Any],
        projection: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        collection = self.get_collection()
        return await collection.distinct(
            field, query, projection=projection or self.get_projection()
        )

    async def find_by_query(
        self, query: dict, projection: Optional[Dict[str, Any]] = None
    ) -> Optional[T]:
        collection = self.get_collection()
        if document := await collection.find_one(
            query, projection=projection or self.get_projection()
        ):
            return self._model_class(**document)
        return None

    async def find_by_id(
        self, document_id: str, projection: Optional[Dict[str, Any]] = None
    ) -> Optional[T]:
        collection = self.get_collection()
        if document := await collection.find_one(
            {"_id": ObjectId(document_id)},
            projection=projection or self.get_projection(),
        ):
            return self._model_class(**document)
        return None

    async def save(self, model: T) -> Optional[T]:
        collection = self.get_collection()
        raw_model = model.model_dump(by_alias=True, exclude_none=True)

        if id_model := raw_model.get("_id", raw_model.get("id")):
            await collection.update_one(
                {"_id": ObjectId(id_model)}, {"$set": raw_model}
            )  # noqa: E501
            return await self.find_by_id(model.id)

        document: InsertOneResult = await collection.insert_one(raw_model)

        return await self.find_by_id(str(document.inserted_id))

    async def bulk_create(self, models: List[T]) -> List[ObjectId]:
        raw_models = [model.model_dump(exclude_none=True) for model in models]
        result: InsertManyResult = await self.get_collection().insert_many(
            raw_models
        )  # noqa: E501
        return result.inserted_ids

    async def delete(self, object_id: Union[str, ObjectId]) -> bool:
        collection = self.get_collection()
        if isinstance(object_id, str):
            object_id = ObjectId(object_id)

        result: DeleteResult = await collection.delete_one({"_id": object_id})

        if result.deleted_count == 1:
            return True
        return False
    
    async def bulk_delete(self, query: Dict[str, Any]) -> bool:
        collection = self.get_collection()
        result: DeleteResult = await collection.delete_many(query)
        return result.deleted_count > 0
    
    async def bulk_update(self, query: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
        collection = self.get_collection()
        result = await collection.update_many(query, {"$set": update_data})
        return result.modified_count > 0