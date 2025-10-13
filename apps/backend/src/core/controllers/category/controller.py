from typing import List, Optional, Dict, Any
from fastapi import HTTPException, Depends, Response
from core.config import settings
from core.auth_utils import verify_auth
from core.db import prisma
from core.controllers.category.io import (
    CategoryCreateInput,
    CategoryUpdateInput,
    CategoryOutput,
    CategoryTreeOutput,
    CategoryListInput
)


class CategoryController:

    async def create(self, data: CategoryCreateInput, email: str = Depends(verify_auth)) -> CategoryOutput:
        """Tạo category mới"""
        try:
            # Kiểm tra slug đã tồn tại chưa
            existing = await prisma.category.find_unique(where={"slug": data.slug})
            if existing:
                raise HTTPException(status_code=400, detail="Slug đã tồn tại")

            # Kiểm tra parent category nếu có
            if data.parent_id:
                parent = await prisma.category.find_unique(where={"id": data.parent_id})
                if not parent:
                    raise HTTPException(status_code=400, detail="Parent category không tồn tại")

            # Tạo category
            category = await prisma.category.create(
                data={
                    "name": data.name,
                    "slug": data.slug,
                    "description": data.description,
                    "image": data.image,
                    "order": data.order,
                    "isActive": data.is_active,
                    "parentId": data.parent_id,
                }
            )

            return CategoryOutput.from_prisma(category)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi tạo category: {str(e)}")

    async def get(self, category_id: int, email: str = Depends(verify_auth)) -> CategoryOutput:
        """Lấy thông tin category theo ID"""
        try:
            category = await prisma.category.find_unique(
                where={"id": category_id},
                include={"parent": True, "children": True}
            )
            if not category:
                raise HTTPException(status_code=404, detail="Category không tồn tại")

            return CategoryOutput.from_prisma(category)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi lấy category: {str(e)}")

    async def get_by_slug(self, slug: str, email: str = Depends(verify_auth)) -> CategoryOutput:
        """Lấy thông tin category theo slug"""
        try:
            category = await prisma.category.find_unique(
                where={"slug": slug},
                include={"parent": True, "children": True}
            )
            if not category:
                raise HTTPException(status_code=404, detail="Category không tồn tại")

            return CategoryOutput.from_prisma(category)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi lấy category: {str(e)}")

    async def list(self, parent_id: Optional[int] = None, only_root: bool = False, is_active: Optional[bool] = None, email: str = Depends(verify_auth)) -> List[CategoryOutput]:
        """Lấy danh sách categories"""
        try:
            where_clause = {}
            
            if parent_id is not None:
                where_clause["parentId"] = parent_id
            elif only_root:
                where_clause["parentId"] = None
                
            if is_active is not None:
                where_clause["isActive"] = is_active

            categories = await prisma.category.find_many(
                where=where_clause,
                include={"parent": True, "children": True},
                order={"order": "asc"}
            )

            return [CategoryOutput.from_prisma(cat) for cat in categories]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi lấy danh sách categories: {str(e)}")

    async def get_tree(self, email: str = Depends(verify_auth)) -> List[CategoryTreeOutput]:
        """Lấy cây category đầy đủ"""
        try:
            # Lấy tất cả categories
            categories = await prisma.category.find_many(
                where={"isActive": True},
                include={"parent": True, "children": True},
                order={"order": "asc"}
            )

            # Xây dựng cây
            category_dict = {}
            root_categories = []

            # Tạo dictionary để truy cập nhanh
            for cat in categories:
                category_dict[cat.id] = CategoryTreeOutput.from_prisma(cat)
                category_dict[cat.id].children = []

            # Xây dựng cây
            for cat in categories:
                if cat.parentId is None:
                    root_categories.append(category_dict[cat.id])
                else:
                    if cat.parentId in category_dict:
                        category_dict[cat.parentId].children.append(category_dict[cat.id])

            return root_categories
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi lấy cây categories: {str(e)}")

    async def update(self, category_id: int, data: CategoryUpdateInput, email: str = Depends(verify_auth)) -> CategoryOutput:
        """Cập nhật category"""
        try:
            # Kiểm tra category tồn tại
            existing = await prisma.category.find_unique(where={"id": category_id})
            if not existing:
                raise HTTPException(status_code=404, detail="Category không tồn tại")

            # Kiểm tra slug đã tồn tại chưa (nếu thay đổi)
            if data.slug and data.slug != existing.slug:
                slug_exists = await prisma.category.find_unique(where={"slug": data.slug})
                if slug_exists:
                    raise HTTPException(status_code=400, detail="Slug đã tồn tại")

            # Kiểm tra parent category nếu có
            if data.parent_id:
                if data.parent_id == category_id:
                    raise HTTPException(status_code=400, detail="Category không thể là parent của chính nó")
                
                parent = await prisma.category.find_unique(where={"id": data.parent_id})
                if not parent:
                    raise HTTPException(status_code=400, detail="Parent category không tồn tại")

            # Cập nhật category
            update_data = {}
            if data.name is not None:
                update_data["name"] = data.name
            if data.slug is not None:
                update_data["slug"] = data.slug
            if data.description is not None:
                update_data["description"] = data.description
            if data.image is not None:
                update_data["image"] = data.image
            if data.order is not None:
                update_data["order"] = data.order
            if data.is_active is not None:
                update_data["isActive"] = data.is_active
            if data.parent_id is not None:
                update_data["parentId"] = data.parent_id

            category = await prisma.category.update(
                where={"id": category_id},
                data=update_data,
                include={"parent": True, "children": True}
            )

            return CategoryOutput.from_prisma(category)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi cập nhật category: {str(e)}")

    async def delete(self, category_id: int, email: str = Depends(verify_auth)) -> Dict[str, str]:
        """Xóa category"""
        try:
            # Kiểm tra category tồn tại
            existing = await prisma.category.find_unique(
                where={"id": category_id},
                include={"children": True}
            )
            if not existing:
                raise HTTPException(status_code=404, detail="Category không tồn tại")

            # Kiểm tra có children không
            if existing.children:
                raise HTTPException(status_code=400, detail="Không thể xóa category có children. Hãy xóa children trước.")

            # Xóa category
            await prisma.category.delete(where={"id": category_id})

            return {"message": "Category đã được xóa thành công"}
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi xóa category: {str(e)}")

    async def move_to_parent(self, category_id: int, new_parent_id: Optional[int] = None, email: str = Depends(verify_auth)) -> CategoryOutput:
        """Di chuyển category sang parent khác"""
        try:
            # Kiểm tra category tồn tại
            existing = await prisma.category.find_unique(where={"id": category_id})
            if not existing:
                raise HTTPException(status_code=404, detail="Category không tồn tại")

            # Kiểm tra parent mới nếu có
            if new_parent_id:
                if new_parent_id == category_id:
                    raise HTTPException(status_code=400, detail="Category không thể là parent của chính nó")
                
                parent = await prisma.category.find_unique(where={"id": new_parent_id})
                if not parent:
                    raise HTTPException(status_code=400, detail="Parent category không tồn tại")

            # Cập nhật parent
            category = await prisma.category.update(
                where={"id": category_id},
                data={"parentId": new_parent_id},
                include={"parent": True, "children": True}
            )

            return CategoryOutput.from_prisma(category)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi di chuyển category: {str(e)}")

    async def reorder(self, category_ids: List[int], email: str = Depends(verify_auth)) -> Dict[str, str]:
        """Sắp xếp lại thứ tự categories"""
        try:
            # Cập nhật order cho từng category
            for index, category_id in enumerate(category_ids):
                await prisma.category.update(
                    where={"id": category_id},
                    data={"order": index}
                )

            return {"message": "Thứ tự categories đã được cập nhật"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi sắp xếp categories: {str(e)}")

    async def sitemap(self) -> Response:
        try:
            cats = await prisma.category.find_many(where={"isActive": True}, order={"updatedAt": "desc"}, take=5000)
            urls = []
            for c in cats:
                loc = f"{settings.site_base_url}/categories/slug/{c.slug}"
                lastmod = c.updatedAt.date().isoformat()
                urls.append(f"<url><loc>{loc}</loc><lastmod>{lastmod}</lastmod><changefreq>weekly</changefreq><priority>0.5</priority></url>")
            xmlset = (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"
                + "".join(urls) +
                "</urlset>"
            )
            return Response(content=xmlset, media_type="application/xml; charset=utf-8")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi tạo sitemap categories: {str(e)}")

    # Public endpoints (read-only)
    async def public_list(self, only_root: bool = False, is_active: bool = True) -> List[CategoryOutput]:
        try:
            where_clause: Dict[str, Any] = {}
            if is_active is not None:
                where_clause["isActive"] = is_active
            if only_root:
                where_clause["parentId"] = None
            cats = await prisma.category.find_many(
                where=where_clause,
                include={"parent": True, "children": True},
                order={"order": "asc"},
            )
            return [CategoryOutput.from_prisma(c) for c in cats]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi lấy categories (public): {str(e)}")

    async def public_get_by_slug(self, slug: str) -> CategoryOutput:
        try:
            cat = await prisma.category.find_first(
                where={"slug": slug, "isActive": True},
                include={"parent": True, "children": True},
            )
            if not cat:
                raise HTTPException(status_code=404, detail="Category không tồn tại hoặc inactive")
            return CategoryOutput.from_prisma(cat)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi lấy category (public): {str(e)}")
