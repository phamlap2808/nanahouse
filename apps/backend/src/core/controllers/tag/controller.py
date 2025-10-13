from typing import List, Optional, Dict, Any
from fastapi import HTTPException, Depends, Response
from core.config import settings
from core.auth_utils import verify_auth
from core.db import prisma
from core.controllers.tag.io import (
    TagCreateInput,
    TagUpdateInput,
    TagOutput,
    TagListInput
)


class TagController:

    async def create(self, data: TagCreateInput, email: str = Depends(verify_auth)) -> TagOutput:
        """Tạo tag mới"""
        try:
            # Kiểm tra slug đã tồn tại chưa
            existing = await prisma.tag.find_unique(where={"slug": data.slug})
            if existing:
                raise HTTPException(status_code=400, detail="Slug đã tồn tại")

            # Kiểm tra name đã tồn tại chưa
            name_exists = await prisma.tag.find_unique(where={"name": data.name})
            if name_exists:
                raise HTTPException(status_code=400, detail="Tên tag đã tồn tại")

            # Tạo tag
            tag = await prisma.tag.create(
                data={
                    "name": data.name,
                    "slug": data.slug,
                    "description": data.description,
                    "color": data.color,
                }
            )

            return TagOutput.from_prisma(tag)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi tạo tag: {str(e)}")

    async def get(self, tag_id: int, email: str = Depends(verify_auth)) -> TagOutput:
        """Lấy thông tin tag theo ID"""
        try:
            tag = await prisma.tag.find_unique(
                where={"id": tag_id},
                include={
                    "postTags": {"include": {"post": True}},
                    "productTags": {"include": {"product": True}}
                }
            )
            if not tag:
                raise HTTPException(status_code=404, detail="Tag không tồn tại")

            return TagOutput.from_prisma(tag)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi lấy tag: {str(e)}")

    async def get_by_slug(self, slug: str, email: str = Depends(verify_auth)) -> TagOutput:
        """Lấy thông tin tag theo slug"""
        try:
            tag = await prisma.tag.find_unique(
                where={"slug": slug},
                include={
                    "postTags": {"include": {"post": True}},
                    "productTags": {"include": {"product": True}}
                }
            )
            if not tag:
                raise HTTPException(status_code=404, detail="Tag không tồn tại")

            return TagOutput.from_prisma(tag)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi lấy tag: {str(e)}")

    async def list(self, 
                  search: Optional[str] = None,
                  color: Optional[str] = None,
                  page: int = 1,
                  limit: int = 20,
                  email: str = Depends(verify_auth)) -> List[TagOutput]:
        """Lấy danh sách tags với các tùy chọn lọc"""
        try:
            where_clause = {}
            
            if search:
                where_clause["OR"] = [
                    {"name": {"contains": search}},
                    {"description": {"contains": search}}
                ]
            if color:
                where_clause["color"] = color

            # Tính offset cho pagination
            offset = (page - 1) * limit

            tags = await prisma.tag.find_many(
                where=where_clause,
                include={
                    "postTags": {"include": {"post": True}},
                    "productTags": {"include": {"product": True}}
                },
                order={"name": "asc"},
                skip=offset,
                take=limit
            )

            return [TagOutput.from_prisma(tag) for tag in tags]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi lấy danh sách tags: {str(e)}")

    async def update(self, tag_id: int, data: TagUpdateInput, email: str = Depends(verify_auth)) -> TagOutput:
        """Cập nhật tag"""
        try:
            # Kiểm tra tag tồn tại
            existing = await prisma.tag.find_unique(where={"id": tag_id})
            if not existing:
                raise HTTPException(status_code=404, detail="Tag không tồn tại")

            # Kiểm tra slug đã tồn tại chưa (nếu thay đổi)
            if data.slug and data.slug != existing.slug:
                slug_exists = await prisma.tag.find_unique(where={"slug": data.slug})
                if slug_exists:
                    raise HTTPException(status_code=400, detail="Slug đã tồn tại")

            # Kiểm tra name đã tồn tại chưa (nếu thay đổi)
            if data.name and data.name != existing.name:
                name_exists = await prisma.tag.find_unique(where={"name": data.name})
                if name_exists:
                    raise HTTPException(status_code=400, detail="Tên tag đã tồn tại")

            # Cập nhật tag
            update_data = {}
            if data.name is not None:
                update_data["name"] = data.name
            if data.slug is not None:
                update_data["slug"] = data.slug
            if data.description is not None:
                update_data["description"] = data.description
            if data.color is not None:
                update_data["color"] = data.color

            tag = await prisma.tag.update(
                where={"id": tag_id},
                data=update_data,
                include={
                    "postTags": {"include": {"post": True}},
                    "productTags": {"include": {"product": True}}
                }
            )

            return TagOutput.from_prisma(tag)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi cập nhật tag: {str(e)}")

    async def delete(self, tag_id: int, email: str = Depends(verify_auth)) -> Dict[str, str]:
        """Xóa tag"""
        try:
            # Kiểm tra tag tồn tại
            existing = await prisma.tag.find_unique(where={"id": tag_id})
            if not existing:
                raise HTTPException(status_code=404, detail="Tag không tồn tại")

            # Xóa tag (cascade sẽ xóa postTags)
            await prisma.tag.delete(where={"id": tag_id})

            return {"message": "Tag đã được xóa thành công"}
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi xóa tag: {str(e)}")

    async def get_popular(self, limit: int = 10, email: str = Depends(verify_auth)) -> List[TagOutput]:
        """Lấy danh sách tags phổ biến (có nhiều posts nhất)"""
        try:
            # Lấy tags với số lượng posts
            tags = await prisma.tag.find_many(
                include={
                    "postTags": True,
                    "productTags": True,
                    "_count": {
                        "select": {"postTags": True, "productTags": True}
                    }
                },
                order={"postTags": {"_count": "desc"}},
                take=limit
            )

            return [TagOutput.from_prisma(tag) for tag in tags]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi lấy tags phổ biến: {str(e)}")

    async def get_posts_by_tag(self, tag_id: int, 
                              page: int = 1, 
                              limit: int = 20, 
                              email: str = Depends(verify_auth)) -> List[Dict[str, Any]]:
        """Lấy danh sách posts theo tag"""
        try:
            # Kiểm tra tag tồn tại
            tag = await prisma.tag.find_unique(where={"id": tag_id})
            if not tag:
                raise HTTPException(status_code=404, detail="Tag không tồn tại")

            # Tính offset cho pagination
            offset = (page - 1) * limit

            # Lấy posts qua PostTag
            post_tags = await prisma.posttag.find_many(
                where={"tagId": tag_id},
                include={
                    "post": {
                        "include": {
                            "author": True,
                            "category": True
                        }
                    }
                },
                order={"post": {"createdAt": "desc"}},
                skip=offset,
                take=limit
            )

            # Format kết quả
            posts = []
            for pt in post_tags:
                post_data = {
                    "id": pt.post.id,
                    "title": pt.post.title,
                    "slug": pt.post.slug,
                    "excerpt": pt.post.excerpt,
                    "featured_image": pt.post.featuredImage,
                    "status": pt.post.status,
                    "published_at": pt.post.publishedAt,
                    "view_count": pt.post.viewCount,
                    "like_count": pt.post.likeCount,
                    "author": {
                        "id": pt.post.author.id,
                        "name": pt.post.author.name,
                        "email": pt.post.author.email
                    },
                    "category": {
                        "id": pt.post.category.id,
                        "name": pt.post.category.name,
                        "slug": pt.post.category.slug
                    } if pt.post.category else None,
                    "created_at": pt.post.createdAt,
                    "updated_at": pt.post.updatedAt
                }
                posts.append(post_data)

            return posts
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi lấy posts theo tag: {str(e)}")

    async def merge_tags(self, source_tag_id: int, target_tag_id: int, email: str = Depends(verify_auth)) -> TagOutput:
        """Gộp 2 tags (chuyển tất cả posts từ source sang target)"""
        try:
            # Kiểm tra cả 2 tags tồn tại
            source_tag = await prisma.tag.find_unique(where={"id": source_tag_id})
            target_tag = await prisma.tag.find_unique(where={"id": target_tag_id})
            
            if not source_tag:
                raise HTTPException(status_code=404, detail="Source tag không tồn tại")
            if not target_tag:
                raise HTTPException(status_code=404, detail="Target tag không tồn tại")

            # Lấy tất cả posts của source tag
            source_posts = await prisma.posttag.find_many(
                where={"tagId": source_tag_id},
                select={"postId": True}
            )

            # Chuyển posts sang target tag
            for post_tag in source_posts:
                # Kiểm tra xem post đã có target tag chưa
                existing = await prisma.posttag.find_unique(
                    where={
                        "postId_tagId": {
                            "postId": post_tag.postId,
                            "tagId": target_tag_id
                        }
                    }
                )
                
                if not existing:
                    # Tạo PostTag mới
                    await prisma.posttag.create(
                        data={
                            "postId": post_tag.postId,
                            "tagId": target_tag_id
                        }
                    )

            # Xóa source tag (cascade sẽ xóa PostTags)
            await prisma.tag.delete(where={"id": source_tag_id})

            # Lấy target tag với relationships
            updated_target = await prisma.tag.find_unique(
                where={"id": target_tag_id},
                include={
                    "postTags": {"include": {"post": True}},
                    "productTags": {"include": {"product": True}}
                }
            )

            return TagOutput.from_prisma(updated_target)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi gộp tags: {str(e)}")

    async def get_products_by_tag(self, tag_id: int, 
                                 page: int = 1, 
                                 limit: int = 20, 
                                 email: str = Depends(verify_auth)) -> List[Dict[str, Any]]:
        """Lấy danh sách products theo tag"""
        try:
            # Kiểm tra tag tồn tại
            tag = await prisma.tag.find_unique(where={"id": tag_id})
            if not tag:
                raise HTTPException(status_code=404, detail="Tag không tồn tại")

            # Tính offset cho pagination
            offset = (page - 1) * limit

            # Lấy products qua ProductTag
            product_tags = await prisma.producttag.find_many(
                where={"tagId": tag_id},
                include={
                    "product": {
                        "include": {
                            "category": True
                        }
                    }
                },
                order={"product": {"createdAt": "desc"}},
                skip=offset,
                take=limit
            )

            # Format kết quả
            products = []
            for pt in product_tags:
                product_data = {
                    "id": pt.product.id,
                    "name": pt.product.name,
                    "slug": pt.product.slug,
                    "description": pt.product.description,
                    "short_description": pt.product.shortDescription,
                    "sku": pt.product.sku,
                    "price": pt.product.price,
                    "compare_price": pt.product.comparePrice,
                    "stock": pt.product.stock,
                    "status": pt.product.status,
                    "featured": pt.product.featured,
                    "category": {
                        "id": pt.product.category.id,
                        "name": pt.product.category.name,
                        "slug": pt.product.category.slug
                    } if pt.product.category else None,
                    "created_at": pt.product.createdAt,
                    "updated_at": pt.product.updatedAt
                }
                products.append(product_data)

            return products
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi lấy products theo tag: {str(e)}")

    async def sitemap(self) -> Response:
        try:
            tags = await prisma.tag.find_many(order={"updatedAt": "desc"}, take=5000)
            urls = []
            for t in tags:
                loc = f"{settings.site_base_url}/tags/slug/{t.slug}"
                lastmod = t.updatedAt.date().isoformat()
                urls.append(f"<url><loc>{loc}</loc><lastmod>{lastmod}</lastmod><changefreq>weekly</changefreq><priority>0.4</priority></url>")
            xmlset = (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"
                + "".join(urls) +
                "</urlset>"
            )
            return Response(content=xmlset, media_type="application/xml; charset=utf-8")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi tạo sitemap tags: {str(e)}")
