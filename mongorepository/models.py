from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type
from dataclasses import dataclass, field
from mongorepository.utils.objects import PyObjectId

def date_tzinfo():
    return datetime.now().replace(tzinfo=timezone.utc)
@dataclass
class MongoBaseModel:
    id: Optional[PyObjectId] = field(default=None, repr=False, metadata={"alias": "_id"})
    created: datetime = field(default_factory=date_tzinfo, init=False)
    updated: datetime = field(default_factory=date_tzinfo, init=False)

    __indexes__ = []

    def update_from_model(self, model: Type['MongoBaseModel']) -> None:
        updates = {key: value for key, value in model.__dict__.items() if value is not None}
        for field, value in updates.items():
            setattr(self, field, value)

    @classmethod
    def projection(cls) -> Dict[str, Any]:
        mapper = {}
        for key, value in cls.__annotations__.items():
            field_name = getattr(value, 'alias', key)
            mapper[field_name] = 1
        return mapper
