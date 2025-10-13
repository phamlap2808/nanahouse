from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime


class PostCreateInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Tiêu đề bài viết")
    slug: str = Field(..., min_length=1, max_length=255, description="Slug duy nhất cho bài viết")
    content: str = Field(..., min_length=1, description="Nội dung bài viết (HTML)")
    excerpt: Optional[str] = Field(None, max_length=500, description="Mô tả ngắn")
    featured_image: Optional[str] = Field(None, max_length=500, description="URL hình ảnh đại diện")
    status: str = Field("draft", description="Trạng thái bài viết")
    published_at: Optional[datetime] = Field(None, description="Thời gian xuất bản")
    category_id: Optional[int] = Field(None, description="ID category")
    tag_ids: Optional[List[int]] = Field(None, description="Danh sách ID tags")
    seo_title: Optional[str] = Field(None, max_length=60, description="SEO title")
    seo_description: Optional[str] = Field(None, max_length=160, description="SEO description")
    seo_keywords: Optional[str] = Field(None, max_length=255, description="SEO keywords")
    canonical_url: Optional[str] = Field(None, max_length=500, description="Canonical URL tuyệt đối")

    @validator('slug')
    def validate_slug(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug chỉ được chứa chữ cái, số, dấu gạch ngang và gạch dưới')
        return v.lower()

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ["draft", "published", "archived"]
        if v not in valid_statuses:
            raise ValueError(f'Status phải là một trong: {valid_statuses}')
        return v


class PostUpdateInput(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Tiêu đề bài viết")
    slug: Optional[str] = Field(None, min_length=1, max_length=255, description="Slug duy nhất cho bài viết")
    content: Optional[str] = Field(None, min_length=1, description="Nội dung bài viết (HTML)")
    excerpt: Optional[str] = Field(None, max_length=500, description="Mô tả ngắn")
    featured_image: Optional[str] = Field(None, max_length=500, description="URL hình ảnh đại diện")
    status: Optional[str] = Field(None, description="Trạng thái bài viết")
    published_at: Optional[datetime] = Field(None, description="Thời gian xuất bản")
    category_id: Optional[int] = Field(None, description="ID category")
    tag_ids: Optional[List[int]] = Field(None, description="Danh sách ID tags")
    seo_title: Optional[str] = Field(None, max_length=60, description="SEO title")
    seo_description: Optional[str] = Field(None, max_length=160, description="SEO description")
    seo_keywords: Optional[str] = Field(None, max_length=255, description="SEO keywords")
    canonical_url: Optional[str] = Field(None, max_length=500, description="Canonical URL tuyệt đối")

    @validator('slug')
    def validate_slug(cls, v):
        if v is not None and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug chỉ được chứa chữ cái, số, dấu gạch ngang và gạch dưới')
        return v.lower() if v else v

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ["draft", "published", "archived"]
            if v not in valid_statuses:
                raise ValueError(f'Status phải là một trong: {valid_statuses}')
        return v


class PostListInput(BaseModel):
    category_id: Optional[int] = Field(None, description="Lọc theo category ID")
    status: Optional[str] = Field(None, description="Lọc theo trạng thái")
    author_id: Optional[int] = Field(None, description="Lọc theo tác giả")
    tag_id: Optional[int] = Field(None, description="Lọc theo tag")
    search: Optional[str] = Field(None, description="Tìm kiếm theo tiêu đề, nội dung")
    page: int = Field(1, ge=1, description="Trang")
    limit: int = Field(20, ge=1, le=100, description="Số lượng mỗi trang")


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


class AuthorOutput(BaseModel):
    id: int
    name: Optional[str] = None
    email: str

    @classmethod
    def from_prisma(cls, author):
        if not author:
            return None
        return cls(
            id=author.id,
            name=author.name,
            email=author.email
        )


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
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_prisma(cls, tag):
        return cls(
            id=tag.id,
            name=tag.name,
            slug=tag.slug,
            description=tag.description,
            color=tag.color,
            created_at=tag.createdAt,
            updated_at=tag.updatedAt
        )


class PostOutput(BaseModel):
    id: int
    title: str
    slug: str
    content: str
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    status: str
    published_at: Optional[datetime] = None
    author_id: int
    author: Optional[AuthorOutput] = None
    category_id: Optional[int] = None
    category: Optional[CategoryOutput] = None
    tags: List[TagOutput] = []
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    canonical_url: Optional[str] = None
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
            content=post.content,
            excerpt=post.excerpt,
            featured_image=post.featuredImage,
            status=post.status,
            published_at=post.publishedAt,
            author_id=post.authorId,
            author=AuthorOutput.from_prisma(post.author) if hasattr(post, 'author') else None,
            category_id=post.categoryId,
            category=CategoryOutput.from_prisma(post.category) if hasattr(post, 'category') else None,
            tags=[TagOutput.from_prisma(pt.tag) for pt in post.postTags] if hasattr(post, 'postTags') and post.postTags else [],
            seo_title=post.seoTitle,
            seo_description=post.seoDescription,
            seo_keywords=post.seoKeywords,
            canonical_url=post.canonicalUrl,
            view_count=post.viewCount,
            like_count=post.likeCount,
            created_at=post.createdAt,
            updated_at=post.updatedAt
        )


# Comment IO models
class CommentCreateInput(BaseModel):
    content: str = Field(..., min_length=1, description="Nội dung bình luận")
    parent_id: Optional[int] = Field(None, description="ID comment cha để tạo thread")


class CommentUpdateInput(BaseModel):
    content: Optional[str] = Field(None, min_length=1, description="Nội dung bình luận")
    status: Optional[str] = Field(None, description="Trạng thái bình luận: visible, hidden, pending")

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ["visible", "hidden", "pending"]
            if v not in valid_statuses:
                raise ValueError(f'Status phải là một trong: {valid_statuses}')
        return v


class CommentOutput(BaseModel):
    id: int
    post_id: int
    user_id: Optional[int] = None
    parent_id: Optional[int] = None
    content: str
    status: str
    created_at: datetime
    updated_at: datetime
    children: List["CommentOutput"] = []

    @classmethod
    def from_prisma(cls, cmt, *, include_children: bool = True):
        return cls(
            id=cmt.id,
            post_id=cmt.postId,
            user_id=cmt.userId,
            parent_id=cmt.parentId,
            content=cmt.content,
            status=cmt.status,
            created_at=cmt.createdAt,
            updated_at=cmt.updatedAt,
            children=[cls.from_prisma(child) for child in getattr(cmt, 'children', [])] if include_children and hasattr(cmt, 'children') and cmt.children else []
        )


# Pydantic forward refs for recursive model (v2 uses model_rebuild)
try:
    CommentOutput.model_rebuild()
except Exception:
    CommentOutput.update_forward_refs()
