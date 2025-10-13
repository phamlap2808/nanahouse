from typing import List, Optional, Dict, Any
from fastapi import HTTPException, Depends
from core.auth_utils import verify_auth
from core.db import prisma
from core.controllers.product.io import (
    ProductCreateInput,
    ProductUpdateInput,
    ProductOutput,
    ProductListInput
)


class ProductController:

    async def create(self, data: ProductCreateInput, email: str = Depends(verify_auth)) -> ProductOutput:
        """Tạo product mới"""
        try:
            # Kiểm tra slug đã tồn tại chưa
            existing = await prisma.product.find_unique(where={"slug": data.slug})
            if existing:
                raise HTTPException(status_code=400, detail="Slug đã tồn tại")

            # Kiểm tra SKU đã tồn tại chưa (nếu có)
            if data.sku:
                sku_exists = await prisma.product.find_unique(where={"sku": data.sku})
                if sku_exists:
                    raise HTTPException(status_code=400, detail="SKU đã tồn tại")

            # Kiểm tra category tồn tại
            category = await prisma.category.find_unique(where={"id": data.category_id})
            if not category:
                raise HTTPException(status_code=400, detail="Category không tồn tại")

            # Tạo product
            product = await prisma.product.create(
                data={
                    "name": data.name,
                    "slug": data.slug,
                    "description": data.description,
                    "shortDescription": data.short_description,
                    "sku": data.sku,
                    "price": data.price,
                    "comparePrice": data.compare_price,
                    "cost": data.cost,
                    "weight": data.weight,
                    "dimensions": data.dimensions,
                    "stock": data.stock,
                    "trackStock": data.track_stock,
                    "allowBackorder": data.allow_backorder,
                    "status": data.status,
                    "featured": data.featured,
                    "tags": data.tags,
                    "seoTitle": data.seo_title,
                    "seoDescription": data.seo_description,
                    "categoryId": data.category_id,
                }
            )

            # Thêm tags nếu có
            if hasattr(data, 'tag_ids') and data.tag_ids:
                for tag_id in data.tag_ids:
                    await prisma.producttag.create(
                        data={"productId": product.id, "tagId": tag_id}
                    )

            # Lấy product với relationships
            product_with_relations = await prisma.product.find_unique(
                where={"id": product.id},
                include={
                    "category": True,
                    "productTags": {
                        "include": {"tag": True}
                    }
                }
            )

            return ProductOutput.from_prisma(product_with_relations)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi tạo product: {str(e)}")

    async def get(self, product_id: int, email: str = Depends(verify_auth)) -> ProductOutput:
        """Lấy thông tin product theo ID"""
        try:
            product = await prisma.product.find_unique(
                where={"id": product_id},
                include={
                    "category": True,
                    "productTags": {
                        "include": {"tag": True}
                    }
                }
            )
            if not product:
                raise HTTPException(status_code=404, detail="Product không tồn tại")

            return ProductOutput.from_prisma(product)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi lấy product: {str(e)}")

    async def get_by_slug(self, slug: str, email: str = Depends(verify_auth)) -> ProductOutput:
        """Lấy thông tin product theo slug"""
        try:
            product = await prisma.product.find_unique(
                where={"slug": slug},
                include={
                    "category": True,
                    "productTags": {
                        "include": {"tag": True}
                    }
                }
            )
            if not product:
                raise HTTPException(status_code=404, detail="Product không tồn tại")

            return ProductOutput.from_prisma(product)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi lấy product: {str(e)}")

    async def list(self, 
                   category_id: Optional[int] = None,
                   status: Optional[str] = None,
                   featured: Optional[bool] = None,
                   min_price: Optional[float] = None,
                   max_price: Optional[float] = None,
                   search: Optional[str] = None,
                   page: int = 1,
                   limit: int = 20,
                   email: str = Depends(verify_auth)) -> List[ProductOutput]:
        """Lấy danh sách products với các tùy chọn lọc"""
        try:
            where_clause = {}
            
            if category_id is not None:
                where_clause["categoryId"] = category_id
            if status is not None:
                where_clause["status"] = status
            if featured is not None:
                where_clause["featured"] = featured
            if min_price is not None or max_price is not None:
                price_filter = {}
                if min_price is not None:
                    price_filter["gte"] = min_price
                if max_price is not None:
                    price_filter["lte"] = max_price
                where_clause["price"] = price_filter
            if search:
                where_clause["OR"] = [
                    {"name": {"contains": search}},
                    {"description": {"contains": search}},
                    {"sku": {"contains": search}}
                ]

            # Tính offset cho pagination
            offset = (page - 1) * limit

            products = await prisma.product.find_many(
                where=where_clause,
                include={
                    "category": True,
                    "productTags": {
                        "include": {"tag": True}
                    }
                },
                order={"createdAt": "desc"},
                skip=offset,
                take=limit
            )

            return [ProductOutput.from_prisma(product) for product in products]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi lấy danh sách products: {str(e)}")

    async def update(self, product_id: int, data: ProductUpdateInput, email: str = Depends(verify_auth)) -> ProductOutput:
        """Cập nhật product"""
        try:
            # Kiểm tra product tồn tại
            existing = await prisma.product.find_unique(where={"id": product_id})
            if not existing:
                raise HTTPException(status_code=404, detail="Product không tồn tại")

            # Kiểm tra slug đã tồn tại chưa (nếu thay đổi)
            if data.slug and data.slug != existing.slug:
                slug_exists = await prisma.product.find_unique(where={"slug": data.slug})
                if slug_exists:
                    raise HTTPException(status_code=400, detail="Slug đã tồn tại")

            # Kiểm tra SKU đã tồn tại chưa (nếu thay đổi)
            if data.sku and data.sku != existing.sku:
                sku_exists = await prisma.product.find_unique(where={"sku": data.sku})
                if sku_exists:
                    raise HTTPException(status_code=400, detail="SKU đã tồn tại")

            # Kiểm tra category nếu có
            if data.category_id:
                category = await prisma.category.find_unique(where={"id": data.category_id})
                if not category:
                    raise HTTPException(status_code=400, detail="Category không tồn tại")

            # Cập nhật product
            update_data = {}
            if data.name is not None:
                update_data["name"] = data.name
            if data.slug is not None:
                update_data["slug"] = data.slug
            if data.description is not None:
                update_data["description"] = data.description
            if data.short_description is not None:
                update_data["shortDescription"] = data.short_description
            if data.sku is not None:
                update_data["sku"] = data.sku
            if data.price is not None:
                update_data["price"] = data.price
            if data.compare_price is not None:
                update_data["comparePrice"] = data.compare_price
            if data.cost is not None:
                update_data["cost"] = data.cost
            if data.weight is not None:
                update_data["weight"] = data.weight
            if data.dimensions is not None:
                update_data["dimensions"] = data.dimensions
            if data.stock is not None:
                update_data["stock"] = data.stock
            if data.track_stock is not None:
                update_data["trackStock"] = data.track_stock
            if data.allow_backorder is not None:
                update_data["allowBackorder"] = data.allow_backorder
            if data.status is not None:
                update_data["status"] = data.status
            if data.featured is not None:
                update_data["featured"] = data.featured
            if data.tags is not None:
                update_data["tags"] = data.tags
            if data.seo_title is not None:
                update_data["seoTitle"] = data.seo_title
            if data.seo_description is not None:
                update_data["seoDescription"] = data.seo_description
            if data.category_id is not None:
                update_data["categoryId"] = data.category_id

            product = await prisma.product.update(
                where={"id": product_id},
                data=update_data,
                include={
                    "category": True,
                    "productTags": {
                        "include": {"tag": True}
                    }
                }
            )

            # Cập nhật tags nếu có
            if hasattr(data, 'tag_ids') and data.tag_ids is not None:
                # Xóa tags cũ
                await prisma.producttag.delete_many(where={"productId": product_id})
                # Thêm tags mới
                for tag_id in data.tag_ids:
                    await prisma.producttag.create(
                        data={"productId": product_id, "tagId": tag_id}
                    )

            return ProductOutput.from_prisma(product)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi cập nhật product: {str(e)}")

    async def delete(self, product_id: int, email: str = Depends(verify_auth)) -> Dict[str, str]:
        """Xóa product"""
        try:
            # Kiểm tra product tồn tại
            existing = await prisma.product.find_unique(where={"id": product_id})
            if not existing:
                raise HTTPException(status_code=404, detail="Product không tồn tại")

            # Xóa product
            await prisma.product.delete(where={"id": product_id})

            return {"message": "Product đã được xóa thành công"}
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi xóa product: {str(e)}")

    async def update_stock(self, product_id: int, stock: int, email: str = Depends(verify_auth)) -> ProductOutput:
        """Cập nhật stock của product"""
        try:
            # Kiểm tra product tồn tại
            existing = await prisma.product.find_unique(where={"id": product_id})
            if not existing:
                raise HTTPException(status_code=404, detail="Product không tồn tại")

            # Cập nhật stock
            product = await prisma.product.update(
                where={"id": product_id},
                data={"stock": stock},
                include={
                    "category": True,
                    "productTags": {
                        "include": {"tag": True}
                    }
                }
            )

            return ProductOutput.from_prisma(product)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi cập nhật stock: {str(e)}")

    async def toggle_featured(self, product_id: int, email: str = Depends(verify_auth)) -> ProductOutput:
        """Toggle trạng thái featured của product"""
        try:
            # Kiểm tra product tồn tại
            existing = await prisma.product.find_unique(where={"id": product_id})
            if not existing:
                raise HTTPException(status_code=404, detail="Product không tồn tại")

            # Toggle featured
            product = await prisma.product.update(
                where={"id": product_id},
                data={"featured": not existing.featured},
                include={
                    "category": True,
                    "productTags": {
                        "include": {"tag": True}
                    }
                }
            )

            return ProductOutput.from_prisma(product)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi toggle featured: {str(e)}")

    async def update_status(self, product_id: int, status: str, email: str = Depends(verify_auth)) -> ProductOutput:
        """Cập nhật trạng thái của product"""
        try:
            # Kiểm tra product tồn tại
            existing = await prisma.product.find_unique(where={"id": product_id})
            if not existing:
                raise HTTPException(status_code=404, detail="Product không tồn tại")

            # Validate status
            valid_statuses = ["draft", "active", "inactive", "archived"]
            if status not in valid_statuses:
                raise HTTPException(status_code=400, detail=f"Status không hợp lệ. Chọn một trong: {valid_statuses}")

            # Cập nhật status
            product = await prisma.product.update(
                where={"id": product_id},
                data={"status": status},
                include={
                    "category": True,
                    "productTags": {
                        "include": {"tag": True}
                    }
                }
            )

            return ProductOutput.from_prisma(product)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi cập nhật status: {str(e)}")

    # Public endpoints (read-only)
    async def public_list(self,
                          category_id: Optional[int] = None,
                          featured: Optional[bool] = None,
                          min_price: Optional[float] = None,
                          max_price: Optional[float] = None,
                          search: Optional[str] = None,
                          page: int = 1,
                          limit: int = 20) -> List[ProductOutput]:
        try:
            where_clause: Dict[str, Any] = {"status": "active"}
            if category_id is not None:
                where_clause["categoryId"] = category_id
            if featured is not None:
                where_clause["featured"] = featured
            if min_price is not None or max_price is not None:
                price_filter: Dict[str, Any] = {}
                if min_price is not None:
                    price_filter["gte"] = min_price
                if max_price is not None:
                    price_filter["lte"] = max_price
                where_clause["price"] = price_filter
            if search:
                where_clause["OR"] = [
                    {"name": {"contains": search}},
                    {"description": {"contains": search}},
                    {"sku": {"contains": search}},
                ]
            offset = (page - 1) * limit
            products = await prisma.product.find_many(
                where=where_clause,
                include={"category": True, "productTags": {"include": {"tag": True}}},
                order={"createdAt": "desc"},
                skip=offset,
                take=limit,
            )
            return [ProductOutput.from_prisma(p) for p in products]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi lấy danh sách products (public): {str(e)}")

    async def public_get_by_slug(self, slug: str) -> ProductOutput:
        try:
            product = await prisma.product.find_first(
                where={"slug": slug, "status": "active"},
                include={"category": True, "productTags": {"include": {"tag": True}}},
            )
            if not product:
                raise HTTPException(status_code=404, detail="Product không tồn tại hoặc không active")
            return ProductOutput.from_prisma(product)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi lấy product (public): {str(e)}")
