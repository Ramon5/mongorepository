from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple, Union

import pymongo
from bson import ObjectId
from pymongo.database import Database
from pymongo.results import DeleteResult, InsertManyResult, InsertOneResult

from mongorepository.repositories.base import AbstractRepository, T
from mongorepository.utils.converters import get_converted_entity


class Repository(AbstractRepository[T]):
    def __init__(self, database: Database):
        super().__init__(database)

    def __get_paginated_documents(
        self,
        query: Dict[str, Any],
        sort: List[Tuple[str, int]],
        next_key=Dict[str, Any],
        projection=Dict[str, Any],
    ) -> Dict[str, Any]:  # noqa: E501
        query, next_key_fn = self.generate_pagination_query(
            query, sort, next_key
        )  # noqa: E501

        cursor = (
            self.get_collection()
            .find(query, projection=projection or self.get_projection())
            .sort(sort)
            .limit(self._query_limit)
        )

        documents = [document for document in cursor]  # noqa: E501

        return {
            "total": len(documents),
            "results": documents,
            "next_page": next_key_fn(documents),
        }

    def list_objects(
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
            result = self.__get_paginated_documents(
                query, sort, next_page, projection or self.get_projection()
            )
            self._convert_paginated_results_to_model(result)
            return result

        cursor = collection.find(
            query, projection=projection or self.get_projection()
        ).sort(sort)

        return [
            self._model_class(**get_converted_entity(document)) for document in cursor
        ]

    def list_distinct(
        self,
        field: str,
        query: Dict[str, Any],
        projection: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        collection = self.get_collection()
        return collection.distinct(
            field, query, projection=projection or self.get_projection()
        )

    def find_by_query(
        self, query: dict, projection: Optional[Dict[str, Any]] = None
    ) -> Optional[T]:
        collection = self.get_collection()
        if document := collection.find_one(
            query, projection=projection or self.get_projection()
        ):
            return self._model_class(**get_converted_entity(document))
        return None

    def find_by_id(
        self, document_id: str, projection: Optional[Dict[str, Any]] = None
    ) -> Optional[T]:
        collection = self.get_collection()
        if document := collection.find_one(
            {"_id": ObjectId(document_id)},
            projection=projection or self.get_projection(),
        ):
            return self._model_class(**get_converted_entity(document))
        return None

    def save(self, model: T) -> Optional[T]:
        collection = self.get_collection()
        raw_model = asdict(model)

        if id_model := raw_model.get("_id", raw_model.get("id")):
            collection.update_one(
                {"_id": ObjectId(id_model)}, {"$set": raw_model}
            )  # noqa: E501
            return self.find_by_id(model.id)

        document: InsertOneResult = collection.insert_one(raw_model)

        return self.find_by_id(str(document.inserted_id))

    def bulk_create(self, models: List[T]) -> List[ObjectId]:
        raw_models = [
            {k: v for k, v in asdict(model).items() if v is not None}
            for model in models
        ]
        result: InsertManyResult = self.get_collection().insert_many(
            raw_models
        )  # noqa: E501
        return result.inserted_ids

    def delete(self, object_id: Union[str, ObjectId]) -> bool:
        collection = self.get_collection()
        if isinstance(object_id, str):
            object_id = ObjectId(object_id)

        result: DeleteResult = collection.delete_one({"_id": object_id})

        if result.deleted_count == 1:
            return True
        return False
