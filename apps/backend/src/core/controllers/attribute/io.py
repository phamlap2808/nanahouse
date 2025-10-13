from typing import Optional, List
from pydantic import BaseModel, Field


class CategoryAttributeCreateInput(BaseModel):
    name: str = Field(..., min_length=1)
    type: str = Field("text")
    options: Optional[str] = None
    position: int = 0


class CategoryAttributeUpdateInput(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    options: Optional[str] = None
    position: Optional[int] = None


class CategoryAttributeOutput(BaseModel):
    id: int
    name: str
    type: str
    options: Optional[str]
    position: int

    @classmethod
    def from_prisma(cls, a):
        return cls(
            id=a.id,
            name=a.name,
            type=a.type,
            options=a.options,
            position=a.position,
        )


class ProductAttributeValueSetInput(BaseModel):
    values: List[dict] = Field(..., description="List of {attribute_id, value}")


class ProductAttributeValueOutput(BaseModel):
    attribute_id: int
    value: str


