"""Category management API endpoints."""

import re
import unicodedata
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.permissions import require_admin
from app.core.security import get_current_user
from app.models.category import Category
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryFlat,
    CategoryResponse,
    CategoryUpdate,
)

router = APIRouter(prefix="/categories", tags=["Categories"])


def _slugify(text: str) -> str:
    """Generate a URL-friendly slug from text."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


async def _ensure_unique_slug(db: AsyncSession, slug: str, exclude_id: int | None = None) -> str:
    """Ensure slug is unique, appending suffix if necessary."""
    base_slug = slug
    counter = 1
    while True:
        query = select(Category).where(Category.slug == slug)
        if exclude_id:
            query = query.where(Category.id != exclude_id)
        result = await db.execute(query)
        if not result.scalar_one_or_none():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


def _build_tree(categories: list[Category]) -> list[Category]:
    """Build a tree structure from flat list of categories."""
    by_id = {c.id: c for c in categories}
    roots = []
    for cat in categories:
        if cat.parent_id is None or cat.parent_id not in by_id:
            roots.append(cat)
    return roots


@router.get("/")
async def list_categories(
    tree: bool = Query(False, description="Return nested tree structure"),
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CategoryResponse] | list[CategoryFlat]:
    """List all categories as flat list or nested tree."""
    result = await db.execute(
        select(Category)
        .options(selectinload(Category.children))
        .order_by(Category.sort_order, Category.name)
    )
    categories = result.scalars().unique().all()

    if tree:
        roots = [c for c in categories if c.parent_id is None]
        return [CategoryResponse.model_validate(r) for r in roots]

    return [CategoryFlat.model_validate(c) for c in categories]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single category with its children."""
    result = await db.execute(
        select(Category)
        .options(selectinload(Category.children))
        .where(Category.id == category_id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new category (admin only)."""
    # Validate parent exists if specified
    if data.parent_id is not None:
        parent_result = await db.execute(
            select(Category).where(Category.id == data.parent_id)
        )
        if not parent_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent category not found",
            )

    slug = await _ensure_unique_slug(db, _slugify(data.name))

    category = Category(
        name=data.name,
        slug=slug,
        description=data.description,
        parent_id=data.parent_id,
        sort_order=data.sort_order,
    )
    db.add(category)
    await db.flush()
    await db.refresh(category, attribute_names=["children"])
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing category (admin only)."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    # Prevent setting parent to self or own descendant
    if data.parent_id is not None:
        if data.parent_id == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category cannot be its own parent",
            )
        # Check parent exists
        parent_result = await db.execute(
            select(Category).where(Category.id == data.parent_id)
        )
        parent = parent_result.scalar_one_or_none()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent category not found",
            )
        # Check for circular reference
        check_id = data.parent_id
        visited = {category_id}
        while check_id is not None:
            if check_id in visited:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Circular parent reference detected",
                )
            visited.add(check_id)
            res = await db.execute(select(Category.parent_id).where(Category.id == check_id))
            row = res.one_or_none()
            check_id = row[0] if row else None

    if data.name is not None:
        category.name = data.name
        category.slug = await _ensure_unique_slug(db, _slugify(data.name), exclude_id=category_id)
    if data.description is not None:
        category.description = data.description
    if data.parent_id is not None or (data.parent_id is None and "parent_id" in data.model_fields_set):
        category.parent_id = data.parent_id
    if data.is_active is not None:
        category.is_active = data.is_active
    if data.sort_order is not None:
        category.sort_order = data.sort_order

    db.add(category)
    await db.flush()
    await db.refresh(category)
    await db.refresh(category, attribute_names=["children"])
    return category


@router.put("/{category_id}/image", response_model=CategoryResponse)
async def upload_category_image(
    category_id: int,
    file: UploadFile = File(...),
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Upload or update category image (admin only)."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, GIF, and WebP images are allowed",
        )

    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 2MB",
        )

    ext = file.filename.rsplit(".", 1)[-1] if file.filename else "jpg"
    filename = f"{uuid4().hex}.{ext}"
    upload_dir = Path(__file__).resolve().parents[2] / "uploads" / "categories"
    upload_dir.mkdir(parents=True, exist_ok=True)
    filepath = upload_dir / filename

    with open(filepath, "wb") as f:
        f.write(contents)

    # Delete old image
    if category.image_url:
        old_filename = category.image_url.rsplit("/", 1)[-1]
        old_path = upload_dir / old_filename
        if old_path.exists():
            old_path.unlink()

    category.image_url = f"/uploads/categories/{filename}"
    db.add(category)
    await db.flush()
    await db.refresh(category, attribute_names=["children"])
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a category (admin only). Fails if it has children."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    # Check for children
    children_result = await db.execute(
        select(Category.id).where(Category.parent_id == category_id).limit(1)
    )
    if children_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with sub-categories. Remove children first.",
        )

    await db.delete(category)
    await db.flush()
