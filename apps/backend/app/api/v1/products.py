"""Product management API endpoints with variant support."""

import math
import re
import unicodedata
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func as sa_func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.permissions import require_admin
from app.core.security import get_current_user
from app.models.category import Category
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
    VariantCreate,
    VariantResponse,
    VariantUpdate,
)

router = APIRouter(prefix="/products", tags=["Products"])


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
        query = select(Product).where(Product.slug == slug)
        if exclude_id:
            query = query.where(Product.id != exclude_id)
        result = await db.execute(query)
        if not result.scalar_one_or_none():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1


def _product_query():
    """Base query with eager loading for category and variants."""
    return select(Product).options(
        selectinload(Product.category),
        selectinload(Product.variants),
    )


# --- Product CRUD ---


@router.get("/", response_model=ProductListResponse)
async def list_products(
    search: str | None = Query(None, description="Search by product name"),
    category_id: int | None = Query(None, description="Filter by category"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List products with filtering and pagination."""
    # Build filter conditions
    conditions = []
    if search:
        conditions.append(Product.name.ilike(f"%{search}%"))
    if category_id is not None:
        conditions.append(Product.category_id == category_id)
    if is_active is not None:
        conditions.append(Product.is_active == is_active)

    # Count total
    count_query = select(sa_func.count(Product.id))
    for cond in conditions:
        count_query = count_query.where(cond)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Fetch page
    query = _product_query().order_by(Product.sort_order, Product.name)
    for cond in conditions:
        query = query.where(cond)
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    products = result.scalars().unique().all()

    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total > 0 else 1,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    _current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single product with variants."""
    result = await db.execute(_product_query().where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new product with optional variants (admin only)."""
    # Validate category
    if data.category_id is not None:
        cat_result = await db.execute(select(Category).where(Category.id == data.category_id))
        if not cat_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found"
            )

    slug = await _ensure_unique_slug(db, _slugify(data.name))

    product = Product(
        name=data.name,
        slug=slug,
        sku=data.sku,
        description=data.description,
        price=data.price,
        compare_price=data.compare_price,
        category_id=data.category_id,
        stock_quantity=data.stock_quantity,
        sort_order=data.sort_order,
    )
    db.add(product)
    await db.flush()

    # Create variants if provided
    for v in data.variants:
        variant = ProductVariant(
            product_id=product.id,
            name=v.name,
            sku=v.sku,
            price=v.price,
            compare_price=v.compare_price,
            stock_quantity=v.stock_quantity,
            sort_order=v.sort_order,
        )
        db.add(variant)

    await db.flush()
    await db.refresh(product, attribute_names=["category", "variants"])
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing product (admin only)."""
    result = await db.execute(_product_query().where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Validate category
    if data.category_id is not None:
        cat_result = await db.execute(select(Category).where(Category.id == data.category_id))
        if not cat_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found"
            )

    if data.name is not None:
        product.name = data.name
        product.slug = await _ensure_unique_slug(db, _slugify(data.name), exclude_id=product_id)
    if data.sku is not None:
        product.sku = data.sku
    if data.description is not None:
        product.description = data.description
    if data.price is not None:
        product.price = data.price
    if data.compare_price is not None:
        product.compare_price = data.compare_price
    if data.category_id is not None or (
        data.category_id is None and "category_id" in data.model_fields_set
    ):
        product.category_id = data.category_id
    if data.is_active is not None:
        product.is_active = data.is_active
    if data.stock_quantity is not None:
        product.stock_quantity = data.stock_quantity
    if data.sort_order is not None:
        product.sort_order = data.sort_order

    db.add(product)
    await db.flush()
    await db.refresh(product, attribute_names=["category", "variants"])
    return product


@router.put("/{product_id}/image", response_model=ProductResponse)
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Upload or update product image (admin only)."""
    result = await db.execute(_product_query().where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, GIF, and WebP images are allowed",
        )

    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File size must be less than 2MB"
        )

    ext = file.filename.rsplit(".", 1)[-1] if file.filename else "jpg"
    filename = f"{uuid4().hex}.{ext}"
    upload_dir = Path(__file__).resolve().parents[2] / "uploads" / "products"
    upload_dir.mkdir(parents=True, exist_ok=True)
    filepath = upload_dir / filename

    with open(filepath, "wb") as f:
        f.write(contents)

    # Delete old image
    if product.image_url:
        old_filename = product.image_url.rsplit("/", 1)[-1]
        old_path = upload_dir / old_filename
        if old_path.exists():
            old_path.unlink()

    product.image_url = f"/uploads/products/{filename}"
    db.add(product)
    await db.flush()
    await db.refresh(product, attribute_names=["category", "variants"])
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a product and all its variants (admin only)."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    await db.delete(product)
    await db.flush()


# --- Variant CRUD (nested under product) ---


@router.post("/{product_id}/variants", response_model=VariantResponse, status_code=status.HTTP_201_CREATED)
async def create_variant(
    product_id: int,
    data: VariantCreate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Add a variant to a product (admin only)."""
    prod_result = await db.execute(select(Product).where(Product.id == product_id))
    if not prod_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    variant = ProductVariant(
        product_id=product_id,
        name=data.name,
        sku=data.sku,
        price=data.price,
        compare_price=data.compare_price,
        stock_quantity=data.stock_quantity,
        sort_order=data.sort_order,
    )
    db.add(variant)
    await db.flush()
    await db.refresh(variant)
    return variant


@router.put("/{product_id}/variants/{variant_id}", response_model=VariantResponse)
async def update_variant(
    product_id: int,
    variant_id: int,
    data: VariantUpdate,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update a variant (admin only)."""
    result = await db.execute(
        select(ProductVariant).where(
            ProductVariant.id == variant_id, ProductVariant.product_id == product_id
        )
    )
    variant = result.scalar_one_or_none()
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")

    if data.name is not None:
        variant.name = data.name
    if data.sku is not None:
        variant.sku = data.sku
    if data.price is not None:
        variant.price = data.price
    if data.compare_price is not None:
        variant.compare_price = data.compare_price
    if data.stock_quantity is not None:
        variant.stock_quantity = data.stock_quantity
    if data.is_active is not None:
        variant.is_active = data.is_active
    if data.sort_order is not None:
        variant.sort_order = data.sort_order

    db.add(variant)
    await db.flush()
    await db.refresh(variant)
    return variant


@router.delete("/{product_id}/variants/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_variant(
    product_id: int,
    variant_id: int,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a variant (admin only)."""
    result = await db.execute(
        select(ProductVariant).where(
            ProductVariant.id == variant_id, ProductVariant.product_id == product_id
        )
    )
    variant = result.scalar_one_or_none()
    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
    await db.delete(variant)
    await db.flush()
