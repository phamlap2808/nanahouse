from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime


class ProductCreateInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Tên sản phẩm")
    slug: str = Field(..., min_length=1, max_length=255, description="Slug duy nhất cho sản phẩm")
    description: Optional[str] = Field(None, max_length=5000, description="Mô tả chi tiết")
    short_description: Optional[str] = Field(None, max_length=500, description="Mô tả ngắn")
    sku: Optional[str] = Field(None, max_length=100, description="Mã SKU")
    price: float = Field(..., ge=0, description="Giá bán")
    compare_price: Optional[float] = Field(None, ge=0, description="Giá so sánh")
    cost: Optional[float] = Field(None, ge=0, description="Giá nhập")
    weight: Optional[float] = Field(None, ge=0, description="Trọng lượng (kg)")
    dimensions: Optional[str] = Field(None, max_length=100, description="Kích thước")
    stock: int = Field(0, ge=0, description="Số lượng tồn kho")
    track_stock: bool = Field(True, description="Theo dõi tồn kho")
    allow_backorder: bool = Field(False, description="Cho phép đặt hàng khi hết hàng")
    status: str = Field("draft", description="Trạng thái sản phẩm")
    featured: bool = Field(False, description="Sản phẩm nổi bật")
    tags: Optional[str] = Field(None, description="Tags (JSON array)")
    seo_title: Optional[str] = Field(None, max_length=60, description="SEO title")
    seo_description: Optional[str] = Field(None, max_length=160, description="SEO description")
    category_id: int = Field(..., description="ID category")
    tag_ids: Optional[List[int]] = Field(None, description="Danh sách ID tags")

    @validator('slug')
    def validate_slug(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug chỉ được chứa chữ cái, số, dấu gạch ngang và gạch dưới')
        return v.lower()

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ["draft", "active", "inactive", "archived"]
        if v not in valid_statuses:
            raise ValueError(f'Status phải là một trong: {valid_statuses}')
        return v

    @validator('compare_price')
    def validate_compare_price(cls, v, values):
        if v is not None and 'price' in values and v <= values['price']:
            raise ValueError('Giá so sánh phải lớn hơn giá bán')
        return v


class ProductUpdateInput(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Tên sản phẩm")
    slug: Optional[str] = Field(None, min_length=1, max_length=255, description="Slug duy nhất cho sản phẩm")
    description: Optional[str] = Field(None, max_length=5000, description="Mô tả chi tiết")
    short_description: Optional[str] = Field(None, max_length=500, description="Mô tả ngắn")
    sku: Optional[str] = Field(None, max_length=100, description="Mã SKU")
    price: Optional[float] = Field(None, ge=0, description="Giá bán")
    compare_price: Optional[float] = Field(None, ge=0, description="Giá so sánh")
    cost: Optional[float] = Field(None, ge=0, description="Giá nhập")
    weight: Optional[float] = Field(None, ge=0, description="Trọng lượng (kg)")
    dimensions: Optional[str] = Field(None, max_length=100, description="Kích thước")
    stock: Optional[int] = Field(None, ge=0, description="Số lượng tồn kho")
    track_stock: Optional[bool] = Field(None, description="Theo dõi tồn kho")
    allow_backorder: Optional[bool] = Field(None, description="Cho phép đặt hàng khi hết hàng")
    status: Optional[str] = Field(None, description="Trạng thái sản phẩm")
    featured: Optional[bool] = Field(None, description="Sản phẩm nổi bật")
    tags: Optional[str] = Field(None, description="Tags (JSON array)")
    seo_title: Optional[str] = Field(None, max_length=60, description="SEO title")
    seo_description: Optional[str] = Field(None, max_length=160, description="SEO description")
    category_id: Optional[int] = Field(None, description="ID category")
    tag_ids: Optional[List[int]] = Field(None, description="Danh sách ID tags")

    @validator('slug')
    def validate_slug(cls, v):
        if v is not None and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug chỉ được chứa chữ cái, số, dấu gạch ngang và gạch dưới')
        return v.lower() if v else v

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ["draft", "active", "inactive", "archived"]
            if v not in valid_statuses:
                raise ValueError(f'Status phải là một trong: {valid_statuses}')
        return v


class ProductListInput(BaseModel):
    category_id: Optional[int] = Field(None, description="Lọc theo category ID")
    status: Optional[str] = Field(None, description="Lọc theo trạng thái")
    featured: Optional[bool] = Field(None, description="Lọc theo sản phẩm nổi bật")
    min_price: Optional[float] = Field(None, ge=0, description="Giá tối thiểu")
    max_price: Optional[float] = Field(None, ge=0, description="Giá tối đa")
    search: Optional[str] = Field(None, description="Tìm kiếm theo tên, mô tả, SKU")
    page: int = Field(1, ge=1, description="Trang")
    limit: int = Field(20, ge=1, le=100, description="Số lượng mỗi trang")


class CategoryOutput(BaseModel):
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


class TagOutput(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    color: Optional[str] = None

    @classmethod
    def from_prisma(cls, tag):
        if not tag:
            return None
        return cls(
            id=tag.id,
            name=tag.name,
            slug=tag.slug,
            description=tag.description,
            color=tag.color
        )


class ProductOutput(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    sku: Optional[str] = None
    price: float
    compare_price: Optional[float] = None
    cost: Optional[float] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    stock: int
    track_stock: bool
    allow_backorder: bool
    status: str
    featured: bool
    tags_json: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    category_id: int
    category: Optional[CategoryOutput] = None
    tags: List[TagOutput] = []
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_prisma(cls, product):
        return cls(
            id=product.id,
            name=product.name,
            slug=product.slug,
            description=product.description,
            short_description=product.shortDescription,
            sku=product.sku,
            price=product.price,
            compare_price=product.comparePrice,
            cost=product.cost,
            weight=product.weight,
            dimensions=product.dimensions,
            stock=product.stock,
            track_stock=product.trackStock,
            allow_backorder=product.allowBackorder,
            status=product.status,
            featured=product.featured,
            tags_json=product.tags,
            seo_title=product.seoTitle,
            seo_description=product.seoDescription,
            category_id=product.categoryId,
            category=CategoryOutput.from_prisma(product.category) if hasattr(product, 'category') else None,
            tags=[TagOutput.from_prisma(pt.tag) for pt in product.productTags] if hasattr(product, 'productTags') and product.productTags else [],
            created_at=product.createdAt,
            updated_at=product.updatedAt
        )
