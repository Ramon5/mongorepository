from typing import Any, Dict


def get_converted_entity(data: Dict[str, Any]) -> Dict[str, Any]:
    data["id"] = data.pop("_id")
    return data
