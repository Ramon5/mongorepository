from datetime import datetime, timezone
from typing import Any, Dict, Optional, TypeVar

from pydantic import BaseModel, Field

from mongorepository.models.base import ObjectIdStr

T = TypeVar("T", bound=BaseModel)


def date_tzinfo():
    return datetime.now().replace(tzinfo=timezone.utc)


class MongoBaseModel(BaseModel):
    id: Optional[ObjectIdStr] = Field(alias="_id")
    created: datetime = Field(default_factory=date_tzinfo)
    updated: datetime = Field(default_factory=date_tzinfo)

    def update_from_model(self, model: T) -> None:
        updates = model.dict(exclude_none=True)
        fields = updates.keys()
        for field in fields:
            setattr(self, field, updates[field])

    @classmethod
    def projection(cls) -> Dict[str, Any]:
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
