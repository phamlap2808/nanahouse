from fastapi import HTTPException, Depends
from typing import List
from prisma import Prisma
from core.auth_utils import verify_auth
from .io import (
    ProductMediaCreateInput, ProductMediaUpdateInput, ProductMediaReorderInput, ProductMediaOutput
)

prisma = Prisma()


class ProductMediaController:
    async def list(self, product_id: int, email: str = Depends(verify_auth)) -> List[ProductMediaOutput]:
        product = await prisma.product.find_unique(where={"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        media = await prisma.productmedia.find_many(
            where={"productId": product_id},
            order={"position": "asc"}
        )
        return [ProductMediaOutput.from_prisma(m) for m in media]

    async def create(self, product_id: int, data: ProductMediaCreateInput, email: str = Depends(verify_auth)) -> ProductMediaOutput:
        product = await prisma.product.find_unique(where={"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # If is_primary, unset existing primaries
        if data.is_primary:
            await prisma.productmedia.update_many(
                where={"productId": product_id, "isPrimary": True},
                data={"isPrimary": False}
            )

        # Determine next position if not set
        position = data.position
        if position == 0:
            count = await prisma.productmedia.count(where={"productId": product_id})
            position = count

        m = await prisma.productmedia.create(
            data={
                "productId": product_id,
                "url": data.url,
                "type": data.type,
                "alt": data.alt,
                "isPrimary": data.is_primary,
                "position": position,
            }
        )
        return ProductMediaOutput.from_prisma(m)

    async def update(self, product_id: int, media_id: int, data: ProductMediaUpdateInput, email: str = Depends(verify_auth)) -> ProductMediaOutput:
        m = await prisma.productmedia.find_first(where={"id": media_id, "productId": product_id})
        if not m:
            raise HTTPException(status_code=404, detail="Media not found")
        updated = await prisma.productmedia.update(
            where={"id": media_id},
            data={"alt": data.alt} if data.alt is not None else {}
        )
        return ProductMediaOutput.from_prisma(updated)

    async def delete(self, product_id: int, media_id: int, email: str = Depends(verify_auth)) -> dict:
        m = await prisma.productmedia.find_first(where={"id": media_id, "productId": product_id})
        if not m:
            raise HTTPException(status_code=404, detail="Media not found")
        await prisma.productmedia.delete(where={"id": media_id})
        return {"success": True}

    async def set_primary(self, product_id: int, media_id: int, email: str = Depends(verify_auth)) -> ProductMediaOutput:
        m = await prisma.productmedia.find_first(where={"id": media_id, "productId": product_id})
        if not m:
            raise HTTPException(status_code=404, detail="Media not found")
        await prisma.productmedia.update_many(
            where={"productId": product_id, "isPrimary": True},
            data={"isPrimary": False}
        )
        updated = await prisma.productmedia.update(where={"id": media_id}, data={"isPrimary": True})
        return ProductMediaOutput.from_prisma(updated)

    async def reorder(self, product_id: int, data: ProductMediaReorderInput, email: str = Depends(verify_auth)) -> List[ProductMediaOutput]:
        # Update positions based on the provided order
        for index, mid in enumerate(data.media_ids):
            await prisma.productmedia.update_many(
                where={"id": mid, "productId": product_id},
                data={"position": index}
            )
        media = await prisma.productmedia.find_many(
            where={"productId": product_id},
            order={"position": "asc"}
        )
        return [ProductMediaOutput.from_prisma(m) for m in media]


