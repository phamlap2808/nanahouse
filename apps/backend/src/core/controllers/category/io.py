from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime


class CategoryCreateInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Tên category")
    slug: str = Field(..., min_length=1, max_length=255, description="Slug duy nhất cho category")
    description: Optional[str] = Field(None, max_length=1000, description="Mô tả category")
    image: Optional[str] = Field(None, max_length=500, description="URL hình ảnh")
    order: int = Field(0, description="Thứ tự sắp xếp")
    is_active: bool = Field(True, description="Trạng thái hoạt động")
    parent_id: Optional[int] = Field(None, description="ID parent category")

    @validator('slug')
    def validate_slug(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug chỉ được chứa chữ cái, số, dấu gạch ngang và gạch dưới')
        return v.lower()


class CategoryUpdateInput(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Tên category")
    slug: Optional[str] = Field(None, min_length=1, max_length=255, description="Slug duy nhất cho category")
    description: Optional[str] = Field(None, max_length=1000, description="Mô tả category")
    image: Optional[str] = Field(None, max_length=500, description="URL hình ảnh")
    order: Optional[int] = Field(None, description="Thứ tự sắp xếp")
    is_active: Optional[bool] = Field(None, description="Trạng thái hoạt động")
    parent_id: Optional[int] = Field(None, description="ID parent category")

    @validator('slug')
    def validate_slug(cls, v):
        if v is not None and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug chỉ được chứa chữ cái, số, dấu gạch ngang và gạch dưới')
        return v.lower() if v else v


class CategoryListInput(BaseModel):
    parent_id: Optional[int] = Field(None, description="Lọc theo parent ID")
    only_root: bool = Field(False, description="Chỉ lấy root categories")
    is_active: Optional[bool] = Field(None, description="Lọc theo trạng thái hoạt động")


class CategoryParentOutput(BaseModel):
    id: int
    name: str
    slug: str

    @classmethod
    def from_prisma(cls, category):
        if not category:
            return None
        return cls(
            id=category.id,
            name=category.name,
            slug=category.slug
        )


class CategoryOutput(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    image: Optional[str] = None
    order: int
    is_active: bool
    parent_id: Optional[int] = None
    parent: Optional[CategoryParentOutput] = None
    children: Optional[List['CategoryOutput']] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_prisma(cls, category):
        return cls(
            id=category.id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            image=category.image,
            order=category.order,
            is_active=category.isActive,
            parent_id=category.parentId,
            parent=CategoryParentOutput.from_prisma(category.parent) if hasattr(category, 'parent') else None,
            children=[cls.from_prisma(child) for child in category.children] if hasattr(category, 'children') and category.children else None,
            created_at=category.createdAt,
            updated_at=category.updatedAt
        )


class CategoryTreeOutput(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    image: Optional[str] = None
    order: int
    is_active: bool
    parent_id: Optional[int] = None
    children: List['CategoryTreeOutput'] = []
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_prisma(cls, category):
        return cls(
            id=category.id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            image=category.image,
            order=category.order,
            is_active=category.isActive,
            parent_id=category.parentId,
            children=[],  # Sẽ được populate trong controller
            created_at=category.createdAt,
            updated_at=category.updatedAt
        )


# Update forward references
CategoryOutput.model_rebuild()
CategoryTreeOutput.model_rebuild()
