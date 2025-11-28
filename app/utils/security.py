from pydantic import ValidationError
from fastapi import HTTPException
from typing import Any

def validate_input(data: Any, schema: Any) -> Any:
    try:
        return schema(**data)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())