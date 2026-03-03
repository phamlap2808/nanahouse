"""Pydantic schemas for product and variant management."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.category import CategoryFlat


# --- Variant Schemas ---

class VariantCreate(BaseModel):
    """Schema for creating a product variant."""

    name: str = Field(min_length=1, max_length=255)
    sku: str | None = None
    price: Decimal = Field(ge=0)
    compare_price: Decimal | None = None
    stock_quantity: int = 0
    sort_order: int = 0


class VariantUpdate(BaseModel):
    """Schema for updating a product variant."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    sku: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    compare_price: Decimal | None = None
    stock_quantity: int | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class VariantResponse(BaseModel):
    """Schema for variant data in responses."""

    id: int
    product_id: int
    name: str
    sku: str | None = None
    price: Decimal
    compare_price: Decimal | None = None
    stock_quantity: int
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# --- Product Schemas ---

class ProductCreate(BaseModel):
    """Schema for creating a new product."""

    name: str = Field(min_length=1, max_length=255)
    sku: str | None = None
    description: str | None = None
    price: Decimal = Field(ge=0, default=0)
    compare_price: Decimal | None = None
    category_id: int | None = None
    stock_quantity: int = 0
    sort_order: int = 0
    variants: list[VariantCreate] = []


class ProductUpdate(BaseModel):
    """Schema for updating an existing product."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    sku: str | None = None
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    compare_price: Decimal | None = None
    category_id: int | None = None
    is_active: bool | None = None
    stock_quantity: int | None = None
    sort_order: int | None = None


class ProductResponse(BaseModel):
    """Schema for product data in responses."""

    id: int
    name: str
    slug: str
    sku: str | None = None
    description: str | None = None
    price: Decimal
    compare_price: Decimal | None = None
    image_url: str | None = None
    category_id: int | None = None
    category: CategoryFlat | None = None
    is_active: bool
    stock_quantity: int
    sort_order: int
    variants: list[VariantResponse] = []
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """Paginated product list response."""

    items: list[ProductResponse]
    total: int
    page: int
    size: int
    pages: int
