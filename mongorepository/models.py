from abc import ABC
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type

from bson import ObjectId

from mongorepository.utils.objects import PyObjectId


def date_tzinfo():
    return datetime.now().replace(tzinfo=timezone.utc)


@dataclass(kw_only=True)
class MongoBaseModel(ABC):
    id: Optional[PyObjectId] = field(
        default=None, repr=False, metadata={"alias": "_id"}
    )
    created: datetime = field(default_factory=date_tzinfo)
    updated: datetime = field(default_factory=date_tzinfo)

    __indexes__ = []

    def update_from_model(self, model: Type["MongoBaseModel"]) -> None:
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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MongoBaseModel":
        init_kwargs = {}
        for f in fields(cls):
            field_name = f.name
            dict_key = f.metadata.get("alias", field_name)

            if dict_key not in data:
                continue

            value = data[dict_key]

            if f.type == Optional[PyObjectId] and isinstance(value, str):
                value = PyObjectId(value)

            elif f.type == datetime and isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value)
                except ValueError:
                    pass

            init_kwargs[field_name] = value

        return cls(**init_kwargs)

    def serialize(self) -> Dict[str, Any]:
        raw_dict = asdict(self)
        doc = {}

        for f in fields(self):
            key = f.name
            value = raw_dict[key]

            dict_key = f.metadata.get("alias", key)

            if isinstance(value, ObjectId):
                value = str(value)

            if isinstance(value, datetime):
                value = value.isoformat()

            doc[dict_key] = value

        if doc.get("_id") is None:
            del doc["_id"]

        return doc
