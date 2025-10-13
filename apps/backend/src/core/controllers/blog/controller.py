from typing import List, Optional, Dict, Any
from fastapi import HTTPException, Depends, Response
from datetime import datetime, timezone
from core.config import settings
from core.auth_utils import verify_auth
from core.db import prisma
from core.controllers.blog.io import (
    PostCreateInput,
    PostUpdateInput,
    PostOutput,
    PostListInput,
    TagCreateInput,
    TagUpdateInput,
    TagOutput,
    CommentCreateInput,
    CommentUpdateInput,
    CommentOutput,
)


class BlogController:

    # Post operations
    async def create_post(self, data: PostCreateInput, email: str = Depends(verify_auth)) -> PostOutput:
        """Tạo bài viết mới"""
        try:
            # Kiểm tra slug đã tồn tại chưa
            existing = await prisma.post.find_unique(where={"slug": data.slug})
            if existing:
                raise HTTPException(status_code=400, detail="Slug đã tồn tại")

            # Lấy thông tin author từ email
            author = await prisma.user.find_unique(where={"email": email})
            if not author:
                raise HTTPException(status_code=404, detail="Author không tồn tại")

            # Kiểm tra category nếu có
            if data.category_id:
                category = await prisma.category.find_unique(where={"id": data.category_id})
                if not category:
                    raise HTTPException(status_code=400, detail="Category không tồn tại")

            # Tạo post
            post = await prisma.post.create(
                data={
                    "title": data.title,
                    "slug": data.slug,
                    "content": data.content,
                    "excerpt": data.excerpt,
                    "featuredImage": data.featured_image,
                    "status": data.status,
                    "publishedAt": data.published_at,
                    "canonicalUrl": data.canonical_url,
                    "authorId": author.id,
                    "categoryId": data.category_id,
                    "seoTitle": data.seo_title,
                    "seoDescription": data.seo_description,
                    "seoKeywords": data.seo_keywords,
                }
            )

            # Thêm tags nếu có
            if data.tag_ids:
                for tag_id in data.tag_ids:
                    await prisma.posttag.create(
                        data={"postId": post.id, "tagId": tag_id}
                    )

            # Lấy post với relationships
            post_with_relations = await prisma.post.find_unique(
                where={"id": post.id},
                include={
                    "author": True,
                    "category": True,
                    "postTags": {
                        "include": {"tag": True}
                    }
                }
            )

            return PostOutput.from_prisma(post_with_relations)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi tạo bài viết: {str(e)}")

    async def get_post(self, post_id: int, email: str = Depends(verify_auth)) -> PostOutput:
        """Lấy thông tin bài viết theo ID"""
        try:
            post = await prisma.post.find_unique(
                where={"id": post_id},
                include={
                    "author": True,
                    "category": True,
                    "postTags": {
                        "include": {"tag": True}
                    }
                }
            )
            if not post:
                raise HTTPException(status_code=404, detail="Bài viết không tồn tại")

            return PostOutput.from_prisma(post)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi lấy bài viết: {str(e)}")

    async def get_post_by_slug(self, slug: str, email: str = Depends(verify_auth)) -> PostOutput:
        """Lấy thông tin bài viết theo slug"""
        try:
            post = await prisma.post.find_unique(
                where={"slug": slug},
                include={
                    "author": True,
                    "category": True,
                    "postTags": {
                        "include": {"tag": True}
                    }
                }
            )
            if not post:
                raise HTTPException(status_code=404, detail="Bài viết không tồn tại")

            return PostOutput.from_prisma(post)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi lấy bài viết: {str(e)}")

    async def list_posts(self, 
                        category_id: Optional[int] = None,
                        status: Optional[str] = None,
                        author_id: Optional[int] = None,
                        tag_id: Optional[int] = None,
                        search: Optional[str] = None,
                        page: int = 1,
                        limit: int = 20,
                        email: str = Depends(verify_auth)) -> List[PostOutput]:
        """Lấy danh sách bài viết với các tùy chọn lọc"""
        try:
            where_clause = {}
            
            if category_id is not None:
                where_clause["categoryId"] = category_id
            if status is not None:
                where_clause["status"] = status
            if author_id is not None:
                where_clause["authorId"] = author_id
            if tag_id is not None:
                where_clause["postTags"] = {"some": {"tagId": tag_id}}
            if search:
                where_clause["OR"] = [
                    {"title": {"contains": search}},
                    {"content": {"contains": search}},
                    {"excerpt": {"contains": search}}
                ]

            # Tính offset cho pagination
            offset = (page - 1) * limit

            posts = await prisma.post.find_many(
                where=where_clause,
                include={
                    "author": True,
                    "category": True,
                    "postTags": {
                        "include": {"tag": True}
                    }
                },
                order={"createdAt": "desc"},
                skip=offset,
                take=limit
            )

            return [PostOutput.from_prisma(post) for post in posts]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi lấy danh sách bài viết: {str(e)}")

    async def update_post(self, post_id: int, data: PostUpdateInput, email: str = Depends(verify_auth)) -> PostOutput:
        """Cập nhật bài viết"""
        try:
            # Kiểm tra post tồn tại
            existing = await prisma.post.find_unique(where={"id": post_id})
            if not existing:
                raise HTTPException(status_code=404, detail="Bài viết không tồn tại")

            # Kiểm tra slug đã tồn tại chưa (nếu thay đổi)
            if data.slug and data.slug != existing.slug:
                slug_exists = await prisma.post.find_unique(where={"slug": data.slug})
                if slug_exists:
                    raise HTTPException(status_code=400, detail="Slug đã tồn tại")

            # Kiểm tra category nếu có
            if data.category_id:
                category = await prisma.category.find_unique(where={"id": data.category_id})
                if not category:
                    raise HTTPException(status_code=400, detail="Category không tồn tại")

            # Cập nhật post
            update_data = {}
            if data.title is not None:
                update_data["title"] = data.title
            if data.slug is not None:
                update_data["slug"] = data.slug
            if data.content is not None:
                update_data["content"] = data.content
            if data.excerpt is not None:
                update_data["excerpt"] = data.excerpt
            if data.featured_image is not None:
                update_data["featuredImage"] = data.featured_image
            if data.status is not None:
                update_data["status"] = data.status
            if data.published_at is not None:
                update_data["publishedAt"] = data.published_at
            if data.canonical_url is not None:
                update_data["canonicalUrl"] = data.canonical_url
            if data.category_id is not None:
                update_data["categoryId"] = data.category_id
            if data.seo_title is not None:
                update_data["seoTitle"] = data.seo_title
            if data.seo_description is not None:
                update_data["seoDescription"] = data.seo_description
            if data.seo_keywords is not None:
                update_data["seoKeywords"] = data.seo_keywords

            # Track slug history
            if data.slug is not None and data.slug != existing.slug:
                await prisma.postslughistory.create(data={"postId": post_id, "oldSlug": existing.slug})

            post = await prisma.post.update(
                where={"id": post_id},
                data=update_data,
                include={
                    "author": True,
                    "category": True,
                    "postTags": {
                        "include": {"tag": True}
                    }
                }
            )

            # Cập nhật tags nếu có
            if data.tag_ids is not None:
                # Xóa tags cũ
                await prisma.posttag.delete_many(where={"postId": post_id})
                # Thêm tags mới
                for tag_id in data.tag_ids:
                    await prisma.posttag.create(
                        data={"postId": post_id, "tagId": tag_id}
                    )

            return PostOutput.from_prisma(post)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi cập nhật bài viết: {str(e)}")

    async def delete_post(self, post_id: int, email: str = Depends(verify_auth)) -> Dict[str, str]:
        """Xóa bài viết"""
        try:
            # Kiểm tra post tồn tại
            existing = await prisma.post.find_unique(where={"id": post_id})
            if not existing:
                raise HTTPException(status_code=404, detail="Bài viết không tồn tại")

            # Xóa post (cascade sẽ xóa postTags)
            await prisma.post.delete(where={"id": post_id})

            return {"message": "Bài viết đã được xóa thành công"}
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi xóa bài viết: {str(e)}")

    async def publish_post(self, post_id: int, email: str = Depends(verify_auth)) -> PostOutput:
        """Xuất bản bài viết"""
        try:
            # Kiểm tra post tồn tại
            existing = await prisma.post.find_unique(where={"id": post_id})
            if not existing:
                raise HTTPException(status_code=404, detail="Bài viết không tồn tại")

            # Cập nhật status và publishedAt
            from datetime import datetime, timezone
            post = await prisma.post.update(
                where={"id": post_id},
                data={
                    "status": "published",
                    "publishedAt": datetime.now(timezone.utc)
                },
                include={
                    "author": True,
                    "category": True,
                    "postTags": {
                        "include": {"tag": True}
                    }
                }
            )

            return PostOutput.from_prisma(post)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi xuất bản bài viết: {str(e)}")

    async def increment_view(self, post_id: int, email: str = Depends(verify_auth)) -> Dict[str, str]:
        """Tăng view count cho bài viết"""
        try:
            # Kiểm tra post tồn tại
            existing = await prisma.post.find_unique(where={"id": post_id})
            if not existing:
                raise HTTPException(status_code=404, detail="Bài viết không tồn tại")

            # Tăng view count
            await prisma.post.update(
                where={"id": post_id},
                data={"viewCount": {"increment": 1}}
            )

            return {"message": "View count đã được cập nhật"}
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi cập nhật view count: {str(e)}")

    # Public post endpoints with scheduled publishing filter
    async def public_list_posts(self,
                                category_id: Optional[int] = None,
                                author_id: Optional[int] = None,
                                tag_id: Optional[int] = None,
                                search: Optional[str] = None,
                                page: int = 1,
                                limit: int = 20) -> List[PostOutput]:
        try:
            where_clause: Dict[str, Any] = {
                "status": "published",
                "publishedAt": {"lte": datetime.now(timezone.utc)}
            }
            if category_id is not None:
                where_clause["categoryId"] = category_id
            if author_id is not None:
                where_clause["authorId"] = author_id
            if tag_id is not None:
                where_clause["postTags"] = {"some": {"tagId": tag_id}}
            if search:
                where_clause["OR"] = [
                    {"title": {"contains": search}},
                    {"content": {"contains": search}},
                    {"excerpt": {"contains": search}},
                ]

            offset = (page - 1) * limit
            posts = await prisma.post.find_many(
                where=where_clause,
                include={
                    "author": True,
                    "category": True,
                    "postTags": {"include": {"tag": True}},
                },
                order={"publishedAt": "desc"},
                skip=offset,
                take=limit,
            )
            return [PostOutput.from_prisma(post) for post in posts]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi lấy danh sách bài viết public: {str(e)}")

    async def public_get_post_by_slug(self, slug: str):
        try:
            # Resolve by current slug
            post = await prisma.post.find_first(
                where={
                    "slug": slug,
                    "status": "published",
                    "publishedAt": {"lte": datetime.now(timezone.utc)}
                },
                include={
                    "author": True,
                    "category": True,
                    "postTags": {"include": {"tag": True}},
                },
            )
            # Or resolve by slug history
            if not post:
                hist = await prisma.postslughistory.find_first(
                    where={"oldSlug": slug},
                    include={"post": True}
                )
                if hist and hist.post and hist.post.status == "published" and (hist.post.publishedAt and hist.post.publishedAt <= datetime.now(timezone.utc)):
                    # 301 redirect to new slug canonical path
                    new_slug = hist.post.slug
                    location = f"/api/blog/public/posts/slug/{new_slug}"
                    return Response(status_code=301, headers={"Location": location})

            if not post:
                raise HTTPException(status_code=404, detail="Bài viết không tồn tại hoặc chưa xuất bản")
            return PostOutput.from_prisma(post)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi lấy bài viết public: {str(e)}")

    async def rss_feed(self) -> Response:
        try:
            posts = await prisma.post.find_many(
                where={
                    "status": "published",
                    "publishedAt": {"lte": datetime.now(timezone.utc)}
                },
                include={"author": True},
                order={"publishedAt": "desc"},
                take=50,
            )

            # Basic RSS 2.0 feed
            items_xml: List[str] = []
            for p in posts:
                pub_date = p.publishedAt.isoformat() if p.publishedAt else p.createdAt.isoformat()
                # Try to build a canonical link; fallback to slug path
                link = f"{settings.site_base_url}/blog/posts/slug/{p.slug}"
                title = p.title.replace("&", "&amp;")
                description = (p.excerpt or "").replace("&", "&amp;")
                items_xml.append(
                    f"<item><title>{title}</title><link>{link}</link><guid>{link}</guid><pubDate>{pub_date}</pubDate><description>{description}</description></item>"
                )

            channel = (
                "<channel>"
                "<title>Blog RSS</title>"
                f"<link>{settings.site_base_url}/blog</link>"
                "<description>Tin mới từ blog</description>"
                + "".join(items_xml) +
                "</channel>"
            )
            xml = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?><rss version=\"2.0\">{channel}</rss>"
            return Response(content=xml, media_type="application/rss+xml; charset=utf-8")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi tạo RSS: {str(e)}")

    async def sitemap(self) -> Response:
        try:
            posts = await prisma.post.find_many(
                where={
                    "status": "published",
                    "publishedAt": {"lte": datetime.now(timezone.utc)}
                },
                order={"publishedAt": "desc"},
                take=5000,
            )
            urls: List[str] = []
            now_iso = datetime.now(timezone.utc).date().isoformat()
            for p in posts:
                loc = f"{settings.site_base_url}/blog/public/posts/slug/{p.slug}"
                lastmod = (p.updatedAt or p.publishedAt or p.createdAt).date().isoformat()
                urls.append(f"<url><loc>{loc}</loc><lastmod>{lastmod}</lastmod><changefreq>weekly</changefreq><priority>0.6</priority></url>")
            xmlset = (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"
                + "".join(urls) +
                "</urlset>"
            )
            return Response(content=xmlset, media_type="application/xml; charset=utf-8")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi tạo sitemap: {str(e)}")

    async def sitemap_index(self) -> Response:
        try:
            today = datetime.now(timezone.utc).date().isoformat()
            sitemaps = [
                {"loc": f"{settings.site_base_url}/api/blog/sitemap.xml", "lastmod": today},
                {"loc": f"{settings.site_base_url}/api/tags/sitemap.xml", "lastmod": today},
                {"loc": f"{settings.site_base_url}/api/categories/sitemap.xml", "lastmod": today},
                {"loc": f"{settings.site_base_url}/api/pages/sitemap.xml", "lastmod": today},
            ]
            xml = (
                "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                "<sitemapindex xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"
                + "".join([f"<sitemap><loc>{s['loc']}</loc><lastmod>{s['lastmod']}</lastmod></sitemap>" for s in sitemaps])
                + "</sitemapindex>"
            )
            return Response(content=xml, media_type="application/xml; charset=utf-8")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi tạo sitemap index: {str(e)}")

    async def public_post_structured_data(self, slug: str) -> Dict[str, Any]:
        try:
            post = await prisma.post.find_first(
                where={
                    "slug": slug,
                    "status": "published",
                    "publishedAt": {"lte": datetime.now(timezone.utc)}
                },
                include={"author": True, "category": True},
            )
            if not post:
                raise HTTPException(status_code=404, detail="Bài viết không tồn tại hoặc chưa xuất bản")

            canonical = post.canonicalUrl or f"{settings.site_base_url}/blog/public/posts/slug/{post.slug}"
            data = {
                "@context": "https://schema.org",
                "@type": "BlogPosting",
                "headline": post.title,
                "datePublished": (post.publishedAt or post.createdAt).isoformat(),
                "dateModified": post.updatedAt.isoformat(),
                "author": {
                    "@type": "Person",
                    "name": post.author.name if post.author and post.author.name else post.author.email if post.author else ""
                },
                "image": post.featuredImage,
                "articleSection": post.category.name if post.category else None,
                "mainEntityOfPage": canonical,
                "url": canonical,
                "description": post.excerpt or post.seoDescription,
            }
            # Remove None fields
            return {k: v for k, v in data.items() if v is not None}
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi structured data: {str(e)}")
    # Tag operations
    async def create_tag(self, data: TagCreateInput, email: str = Depends(verify_auth)) -> TagOutput:
        """Tạo tag mới"""
        try:
            # Kiểm tra slug đã tồn tại chưa
            existing = await prisma.tag.find_unique(where={"slug": data.slug})
            if existing:
                raise HTTPException(status_code=400, detail="Slug đã tồn tại")

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

    async def get_tag(self, tag_id: int, email: str = Depends(verify_auth)) -> TagOutput:
        """Lấy thông tin tag theo ID"""
        try:
            tag = await prisma.tag.find_unique(where={"id": tag_id})
            if not tag:
                raise HTTPException(status_code=404, detail="Tag không tồn tại")

            return TagOutput.from_prisma(tag)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi lấy tag: {str(e)}")

    async def list_tags(self, email: str = Depends(verify_auth)) -> List[TagOutput]:
        """Lấy danh sách tags"""
        try:
            tags = await prisma.tag.find_many(
                order={"name": "asc"}
            )

            return [TagOutput.from_prisma(tag) for tag in tags]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi lấy danh sách tags: {str(e)}")

    async def update_tag(self, tag_id: int, data: TagUpdateInput, email: str = Depends(verify_auth)) -> TagOutput:
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
                data=update_data
            )

            return TagOutput.from_prisma(tag)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi cập nhật tag: {str(e)}")

    async def delete_tag(self, tag_id: int, email: str = Depends(verify_auth)) -> Dict[str, str]:
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

    # Comment operations (scoped under posts)
    async def list_post_comments(self, post_id: int, email: str = Depends(verify_auth)) -> List[CommentOutput]:
        try:
            # ensure post exists
            post = await prisma.post.find_unique(where={"id": post_id})
            if not post:
                raise HTTPException(status_code=404, detail="Bài viết không tồn tại")

            comments = await prisma.comment.find_many(
                where={"postId": post_id, "parentId": None},
                include={"children": {"include": {"children": True}}},
                order={"createdAt": "asc"}
            )
            return [CommentOutput.from_prisma(c) for c in comments]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi lấy danh sách bình luận: {str(e)}")

    async def create_post_comment(self, post_id: int, data: CommentCreateInput, email: str = Depends(verify_auth)) -> CommentOutput:
        try:
            user = await prisma.user.find_unique(where={"email": email})
            if not user:
                raise HTTPException(status_code=401, detail="Người dùng không hợp lệ")

            # ensure post exists
            post = await prisma.post.find_unique(where={"id": post_id})
            if not post:
                raise HTTPException(status_code=404, detail="Bài viết không tồn tại")

            # validate parent if provided and belongs to same post
            if data.parent_id is not None:
                parent = await prisma.comment.find_unique(where={"id": data.parent_id})
                if not parent or parent.postId != post_id:
                    raise HTTPException(status_code=400, detail="Comment cha không hợp lệ")

            created = await prisma.comment.create(
                data={
                    "postId": post_id,
                    "userId": user.id,
                    "parentId": data.parent_id,
                    "content": data.content,
                    "status": "visible",
                },
                include={"children": True}
            )
            return CommentOutput.from_prisma(created)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi tạo bình luận: {str(e)}")

    async def update_post_comment(self, post_id: int, comment_id: int, data: CommentUpdateInput, email: str = Depends(verify_auth)) -> CommentOutput:
        try:
            # fetch
            existing = await prisma.comment.find_unique(where={"id": comment_id})
            if not existing or existing.postId != post_id:
                raise HTTPException(status_code=404, detail="Bình luận không tồn tại")

            # only owner or admin can edit: simple check by email==owner
            user = await prisma.user.find_unique(where={"email": email})
            if not user:
                raise HTTPException(status_code=401, detail="Người dùng không hợp lệ")
            if (existing.userId is not None and existing.userId != user.id) and not user.isAdmin:
                raise HTTPException(status_code=403, detail="Không có quyền sửa bình luận")

            update_data: Dict[str, Any] = {}
            if data.content is not None:
                update_data["content"] = data.content
            if data.status is not None:
                update_data["status"] = data.status

            updated = await prisma.comment.update(
                where={"id": comment_id},
                data=update_data,
                include={"children": True}
            )
            return CommentOutput.from_prisma(updated)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi cập nhật bình luận: {str(e)}")

    async def delete_post_comment(self, post_id: int, comment_id: int, email: str = Depends(verify_auth)) -> Dict[str, str]:
        try:
            existing = await prisma.comment.find_unique(where={"id": comment_id})
            if not existing or existing.postId != post_id:
                raise HTTPException(status_code=404, detail="Bình luận không tồn tại")

            user = await prisma.user.find_unique(where={"email": email})
            if not user:
                raise HTTPException(status_code=401, detail="Người dùng không hợp lệ")
            if (existing.userId is not None and existing.userId != user.id) and not user.isAdmin:
                raise HTTPException(status_code=403, detail="Không có quyền xóa bình luận")

            await prisma.comment.delete(where={"id": comment_id})
            return {"message": "Đã xóa bình luận"}
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=f"Lỗi xóa bình luận: {str(e)}")
