from typing import Mapping, Sequence, TypeVar, Generic, Optional

from fastapi import Body
from pydantic import BaseModel

T = TypeVar("T")


class ListOutput(BaseModel, Generic[T]):
    items: Sequence[T]
    total_records: int
    total_pages: int


class BaseResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    error: Optional[str] = None

def wrap_example(examples: Mapping[str, BaseModel]):
    openapi_examples = {}
    for key, value in examples.items():
        openapi_examples[key] = {}
        openapi_examples[key]["value"] = value.model_dump()
    return Body(openapi_examples=openapi_examples)