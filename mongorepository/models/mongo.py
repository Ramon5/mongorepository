from typing import Optional

from pydantic import BaseModel, Field

from mongorepository.models.base import ObjectIdStr


class MongoBaseModel(BaseModel):
    id: Optional[ObjectIdStr] = Field(alias="_id")

    @classmethod
    def projection(cls) -> dict:
        fields = cls.__fields__
        keys = fields.keys()
        mapper = {}

        for key in keys:
            value = fields[key]
            if value.alias:
                mapper[value.alias] = 1
            else:
                mapper[key] = 1

        return mapper
