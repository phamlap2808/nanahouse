from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class CollectionCreateInput(BaseModel):
    title: str = Field(..., min_length=1)
    slug: str = Field(..., min_length=1)
    description: Optional[str] = None
    image: Optional[str] = None
    is_active: bool = True


class CollectionUpdateInput(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    is_active: Optional[bool] = None


class CollectionOutput(BaseModel):
    id: int
    title: str
    slug: str
    description: Optional[str]
    image: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_prisma(cls, c):
        return cls(
            id=c.id,
            title=c.title,
            slug=c.slug,
            description=c.description,
            image=c.image,
            is_active=c.isActive,
            created_at=c.createdAt,
            updated_at=c.updatedAt,
        )


class CollectionProductAddInput(BaseModel):
    product_id: int
    position: int = 0


class CollectionProductReorderInput(BaseModel):
    product_ids: List[int]


