from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type, TypeVar

from mongorepository.utils.objects import PyObjectId

T = TypeVar("T", bound=BaseModel)

def date_tzinfo():
    return datetime.now().replace(tzinfo=timezone.utc)

class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    created: datetime = Field(default_factory=date_tzinfo)
    updated: datetime = Field(default_factory=date_tzinfo)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    __indexes__ = []

    def update_from_model(self, model: T) -> None:
        updates = {
            key: value for key, value in model.__dict__.items() if value is not None
        }
        for field, value in updates.items():
            setattr(self, field, value)

    @classmethod
    def projection(cls) -> Dict[str, Any]:
        mapper = {}
        for key, value in cls.__annotations__.items():
            field_name = getattr(value, "alias", key)
            mapper[field_name] = 1
        return mapper