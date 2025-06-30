from typing import Any
from bson import ObjectId
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue


class PyObjectId(ObjectId):
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.with_info_after_validator_function(
            cls.validate, handler(ObjectId), field_name=handler.field_name
        )

    @classmethod
    def validate(cls, value: Any, info: core_schema.ValidationInfo) -> ObjectId:
        if not cls.is_valid(value):
            raise ValueError("Invalid objectid")
        return ObjectId(value)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: Any, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        json_schema = super().__get_pydantic_json_schema__(core_schema, handler)
        json_schema = handler.resolve_ref_schema({'type': 'string'})
        json_schema.update(examples=['64ca7f4b8450a3bd8767e4a2'])
        return json_schema
