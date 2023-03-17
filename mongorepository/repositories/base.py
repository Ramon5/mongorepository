from typing import Generic, TypeVar

from mongorepository.models.mongo import MongoBaseModel

T = TypeVar("T", bound=MongoBaseModel)


class AbstractRepository(Generic[T]):
    def __init__(self, database):
        self.__database = database
        self.__collection_name = self.Config.collection
        self._paginated = self.__get_pagination_flag()
        self._query_limit = self.__get_query_limit_documents()
        self._model_class = self.__orig_bases__[0].__args__[0]

    def __get_pagination_flag(self) -> bool:
        if hasattr(self.Config, "pagination"):
            return self.Config.pagination or False
        return False

    def __get_query_limit_documents(self):
        if hasattr(self.Config, "pagination"):
            if hasattr(self.Config, "limit"):
                return self.Config.limit
            return 50

    def set_pagination(self, value: bool):
        self._paginated = value
        self._query_limit = 50

    def get_collection(self):
        return self.__database.get_collection(self.__collection_name)

    def get_projection(self) -> dict:
        projection = self._model_class.projection()
        if hasattr(self.Config, "projection"):
            projection = self.Config.projection
        return projection

    def _convert_paginated_results_to_model(self, document: dict) -> None:
        document["results"] = [
            self._model_class(**document) for document in document["results"]
        ]

    def generate_pagination_query(self, query, sort=None, next_key=None):
        sort_field = sort[0][0] if sort else None

        def next_key_fn(items):
            if not items:
                return None
            item = items[-1]
            if sort_field is None:
                return {"_id": item["_id"]}

            return {"_id": item["_id"], sort_field: item[sort_field]}

        if next_key is None:
            return query, next_key_fn

        paginated_query = query.copy()

        if sort is None:
            paginated_query["_id"] = {"$gt": next_key["_id"]}
            return paginated_query, next_key_fn

        sort_operator = "$gt" if sort[0][1] == 1 else "$lt"

        pagination_query = [
            {sort_field: {sort_operator: next_key[sort_field]}},
            {
                "$and": [
                    {sort_field: next_key[sort_field]},
                    {"_id": {sort_operator: next_key["_id"]}},
                ]
            },
        ]

        if "$or" not in paginated_query:
            paginated_query["$or"] = pagination_query
        else:
            paginated_query = {"$and": [query, {"$or": pagination_query}]}

        return paginated_query, next_key_fn
