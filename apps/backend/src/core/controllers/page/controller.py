from fastapi import HTTPException, Depends, Response
from core.config import settings
from typing import List
from prisma import Prisma
from core.auth_utils import verify_auth
from .io import (
    PageCreateInput, PageUpdateInput, PageOutput,
    PageBlockCreateInput, PageBlockUpdateInput, PageBlockReorderInput, PageBlockOutput
)

prisma = Prisma()


class PageController:
    async def list(self, email: str = Depends(verify_auth)) -> List[PageOutput]:
        pages = await prisma.page.find_many(order={"createdAt": "desc"})
        return [PageOutput.from_prisma(p) for p in pages]

    async def create(self, data: PageCreateInput, email: str = Depends(verify_auth)) -> PageOutput:
        p = await prisma.page.create(data={
            "title": data.title,
            "slug": data.slug,
            "content": data.content,
            "status": data.status,
            "publishedAt": data.published_at,
            "metaTitle": data.meta_title,
            "metaDescription": data.meta_description,
        })
        return PageOutput.from_prisma(p)

    async def get(self, page_id: int, email: str = Depends(verify_auth)) -> PageOutput:
        p = await prisma.page.find_unique(where={"id": page_id})
        if not p:
            raise HTTPException(status_code=404, detail="Page not found")
        return PageOutput.from_prisma(p)

    async def update(self, page_id: int, data: PageUpdateInput, email: str = Depends(verify_auth)) -> PageOutput:
        p = await prisma.page.find_unique(where={"id": page_id})
        if not p:
            raise HTTPException(status_code=404, detail="Page not found")
        upd = {}
        if data.title is not None: upd["title"] = data.title
        if data.slug is not None: upd["slug"] = data.slug
        if data.content is not None: upd["content"] = data.content
        if data.status is not None: upd["status"] = data.status
        if data.published_at is not None: upd["publishedAt"] = data.published_at
        if data.meta_title is not None: upd["metaTitle"] = data.meta_title
        if data.meta_description is not None: upd["metaDescription"] = data.meta_description
        p = await prisma.page.update(where={"id": page_id}, data=upd)
        return PageOutput.from_prisma(p)

    async def delete(self, page_id: int, email: str = Depends(verify_auth)) -> dict:
        await prisma.pageblock.delete_many(where={"pageId": page_id})
        await prisma.page.delete(where={"id": page_id})
        return {"success": True}

    # Blocks
    async def list_blocks(self, page_id: int, email: str = Depends(verify_auth)) -> List[PageBlockOutput]:
        page = await prisma.page.find_unique(where={"id": page_id})
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
        bs = await prisma.pageblock.find_many(where={"pageId": page_id}, order={"position": "asc"})
        return [PageBlockOutput.from_prisma(b) for b in bs]

    async def create_block(self, page_id: int, data: PageBlockCreateInput, email: str = Depends(verify_auth)) -> PageBlockOutput:
        page = await prisma.page.find_unique(where={"id": page_id})
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
        pos = data.position
        if pos == 0:
            count = await prisma.pageblock.count(where={"pageId": page_id})
            pos = count
        b = await prisma.pageblock.create(data={
            "pageId": page_id,
            "type": data.type,
            "data": data.data,
            "position": pos,
            "isActive": data.is_active,
        })
        return PageBlockOutput.from_prisma(b)

    async def update_block(self, page_id: int, block_id: int, data: PageBlockUpdateInput, email: str = Depends(verify_auth)) -> PageBlockOutput:
        b = await prisma.pageblock.find_first(where={"id": block_id, "pageId": page_id})
        if not b:
            raise HTTPException(status_code=404, detail="Block not found")
        upd = {}
        if data.type is not None: upd["type"] = data.type
        if data.data is not None: upd["data"] = data.data
        if data.position is not None: upd["position"] = data.position
        if data.is_active is not None: upd["isActive"] = data.is_active
        b = await prisma.pageblock.update(where={"id": block_id}, data=upd)
        return PageBlockOutput.from_prisma(b)

    async def delete_block(self, page_id: int, block_id: int, email: str = Depends(verify_auth)) -> dict:
        await prisma.pageblock.delete_many(where={"id": block_id, "pageId": page_id})
        return {"success": True}

    async def reorder_blocks(self, page_id: int, block_ids: PageBlockReorderInput, email: str = Depends(verify_auth)) -> dict:
        for idx, bid in enumerate(block_ids.block_ids):
            await prisma.pageblock.update_many(where={"id": bid, "pageId": page_id}, data={"position": idx})
        return {"success": True}



    async def sitemap(self) -> Response:
        pages = await prisma.page.find_many(where={"status": "published"}, order={"updatedAt": "desc"}, take=5000)
        urls = []
        for p in pages:
            loc = f"{settings.site_base_url}/pages/{p.slug}"
            lastmod = (p.updatedAt or p.publishedAt or p.createdAt).date().isoformat()
            urls.append(f"<url><loc>{loc}</loc><lastmod>{lastmod}</lastmod><changefreq>monthly</changefreq><priority>0.3</priority></url>")
        xmlset = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
            "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">"
            + "".join(urls) +
            "</urlset>"
        )
        return Response(content=xmlset, media_type="application/xml; charset=utf-8")

    # Public endpoints (read-only)
    async def public_list(self) -> List[PageOutput]:
        pages = await prisma.page.find_many(where={"status": "published"}, order={"publishedAt": "desc"})
        return [PageOutput.from_prisma(p) for p in pages]

    async def public_get_by_slug(self, slug: str) -> PageOutput:
        p = await prisma.page.find_first(where={"slug": slug, "status": "published"})
        if not p:
            raise HTTPException(status_code=404, detail="Page not found or unpublished")
        return PageOutput.from_prisma(p)
