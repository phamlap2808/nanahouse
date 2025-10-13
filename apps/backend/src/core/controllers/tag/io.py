from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class TagCreateInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Tên tag")
    slug: str = Field(..., min_length=1, max_length=100, description="Slug duy nhất cho tag")
    description: Optional[str] = Field(None, max_length=500, description="Mô tả tag")
    color: Optional[str] = Field(None, max_length=7, description="Mã màu hex (VD: #FF0000)")

    @validator('slug')
    def validate_slug(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug chỉ được chứa chữ cái, số, dấu gạch ngang và gạch dưới')
        return v.lower()

    @validator('color')
    def validate_color(cls, v):
        if v is not None and not v.startswith('#') and len(v) != 7:
            raise ValueError('Mã màu phải có định dạng #RRGGBB')
        return v


class TagUpdateInput(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Tên tag")
    slug: Optional[str] = Field(None, min_length=1, max_length=100, description="Slug duy nhất cho tag")
    description: Optional[str] = Field(None, max_length=500, description="Mô tả tag")
    color: Optional[str] = Field(None, max_length=7, description="Mã màu hex (VD: #FF0000)")

    @validator('slug')
    def validate_slug(cls, v):
        if v is not None and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug chỉ được chứa chữ cái, số, dấu gạch ngang và gạch dưới')
        return v.lower() if v else v

    @validator('color')
    def validate_color(cls, v):
        if v is not None and not v.startswith('#') and len(v) != 7:
            raise ValueError('Mã màu phải có định dạng #RRGGBB')
        return v


class TagListInput(BaseModel):
    search: Optional[str] = Field(None, description="Tìm kiếm theo tên, mô tả")
    color: Optional[str] = Field(None, description="Lọc theo màu")
    page: int = Field(1, ge=1, description="Trang")
    limit: int = Field(20, ge=1, le=100, description="Số lượng mỗi trang")


class PostSummaryOutput(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    status: str
    published_at: Optional[datetime] = None
    view_count: int
    like_count: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_prisma(cls, post):
        return cls(
            id=post.id,
            title=post.title,
            slug=post.slug,
            excerpt=post.excerpt,
            featured_image=post.featuredImage,
            status=post.status,
            published_at=post.publishedAt,
            view_count=post.viewCount,
            like_count=post.likeCount,
            created_at=post.createdAt,
            updated_at=post.updatedAt
        )


class TagOutput(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    color: Optional[str] = None
    post_count: int = 0
    product_count: int = 0
    posts: List[PostSummaryOutput] = []
    products: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_prisma(cls, tag):
        # Tính số lượng posts và products
        post_count = 0
        product_count = 0
        posts = []
        products = []
        
        if hasattr(tag, 'postTags') and tag.postTags:
            post_count = len(tag.postTags)
            posts = [PostSummaryOutput.from_prisma(pt.post) for pt in tag.postTags if hasattr(pt, 'post') and pt.post]
        elif hasattr(tag, '_count') and hasattr(tag._count, 'postTags'):
            post_count = tag._count.postTags

        if hasattr(tag, 'productTags') and tag.productTags:
            product_count = len(tag.productTags)
            products = [{
                "id": pt.product.id,
                "name": pt.product.name,
                "slug": pt.product.slug,
                "price": pt.product.price,
                "status": pt.product.status,
                "featured": pt.product.featured
            } for pt in tag.productTags if hasattr(pt, 'product') and pt.product]
        elif hasattr(tag, '_count') and hasattr(tag._count, 'productTags'):
            product_count = tag._count.productTags

        return cls(
            id=tag.id,
            name=tag.name,
            slug=tag.slug,
            description=tag.description,
            color=tag.color,
            post_count=post_count,
            product_count=product_count,
            posts=posts,
            products=products,
            created_at=tag.createdAt,
            updated_at=tag.updatedAt
        )


class TagMergeInput(BaseModel):
    source_tag_id: int = Field(..., description="ID tag nguồn")
    target_tag_id: int = Field(..., description="ID tag đích")
