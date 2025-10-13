from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class PageCreateInput(BaseModel):
    title: str
    slug: str
    content: Optional[str] = None
    status: str = "draft"
    published_at: Optional[datetime] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class PageUpdateInput(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None
    published_at: Optional[datetime] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class PageOutput(BaseModel):
    id: int
    title: str
    slug: str
    content: Optional[str]
    status: str
    published_at: Optional[datetime]
    meta_title: Optional[str]
    meta_description: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_prisma(cls, p):
        return cls(
            id=p.id,
            title=p.title,
            slug=p.slug,
            content=p.content,
            status=p.status,
            published_at=p.publishedAt,
            meta_title=p.metaTitle,
            meta_description=p.metaDescription,
            created_at=p.createdAt,
            updated_at=p.updatedAt,
        )


class PageBlockCreateInput(BaseModel):
    type: str
    data: Optional[str] = None
    position: int = 0
    is_active: bool = True


class PageBlockUpdateInput(BaseModel):
    type: Optional[str] = None
    data: Optional[str] = None
    position: Optional[int] = None
    is_active: Optional[bool] = None


class PageBlockReorderInput(BaseModel):
    block_ids: List[int]


class PageBlockOutput(BaseModel):
    id: int
    type: str
    data: Optional[str]
    position: int
    is_active: bool

    @classmethod
    def from_prisma(cls, b):
        return cls(
            id=b.id,
            type=b.type,
            data=b.data,
            position=b.position,
            is_active=b.isActive,
        )


