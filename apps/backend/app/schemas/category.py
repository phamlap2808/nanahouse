"""Pydantic schemas for category management."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    """Schema for creating a new category."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    parent_id: int | None = None
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    parent_id: int | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class CategoryResponse(BaseModel):
    """Schema for category data in responses (supports recursive tree)."""

    id: int
    name: str
    slug: str
    description: str | None = None
    image_url: str | None = None
    parent_id: int | None = None
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime | None = None
    children: list[CategoryResponse] = []

    model_config = {"from_attributes": True}


class CategoryFlat(BaseModel):
    """Flat category response without children (for list views)."""

    id: int
    name: str
    slug: str
    description: str | None = None
    image_url: str | None = None
    parent_id: int | None = None
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
