from typing import Optional, List
from pydantic import BaseModel, Field


class ProductMediaCreateInput(BaseModel):
    url: str = Field(..., min_length=1)
    type: str = Field("image")
    alt: Optional[str] = None
    is_primary: bool = False
    position: int = 0


class ProductMediaUpdateInput(BaseModel):
    alt: Optional[str] = None


class ProductMediaReorderInput(BaseModel):
    media_ids: List[int] = Field(..., description="Ordered list of media IDs")


class ProductMediaOutput(BaseModel):
    id: int
    url: str
    type: str
    alt: Optional[str]
    is_primary: bool
    position: int

    @classmethod
    def from_prisma(cls, m):
        return cls(
            id=m.id,
            url=m.url,
            type=m.type,
            alt=m.alt,
            is_primary=m.isPrimary,
            position=m.position,
        )


