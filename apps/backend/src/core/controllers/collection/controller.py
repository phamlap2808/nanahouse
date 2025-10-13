from fastapi import HTTPException, Depends
from prisma import Prisma
from core.auth_utils import verify_auth
from .io import (
    CollectionCreateInput, CollectionUpdateInput, CollectionOutput,
    CollectionProductAddInput, CollectionProductReorderInput
)

prisma = Prisma()


class CollectionController:
    async def list(self, email: str = Depends(verify_auth)) -> list[CollectionOutput]:
        cols = await prisma.collection.find_many(order={"createdAt": "desc"})
        return [CollectionOutput.from_prisma(c) for c in cols]

    async def create(self, data: CollectionCreateInput, email: str = Depends(verify_auth)) -> CollectionOutput:
        c = await prisma.collection.create(
            data={
                "title": data.title,
                "slug": data.slug,
                "description": data.description,
                "image": data.image,
                "isActive": data.is_active,
            }
        )
        return CollectionOutput.from_prisma(c)

    async def get(self, collection_id: int, email: str = Depends(verify_auth)) -> CollectionOutput:
        c = await prisma.collection.find_unique(where={"id": collection_id})
        if not c:
            raise HTTPException(status_code=404, detail="Collection not found")
        return CollectionOutput.from_prisma(c)

    async def update(self, collection_id: int, data: CollectionUpdateInput, email: str = Depends(verify_auth)) -> CollectionOutput:
        c = await prisma.collection.find_unique(where={"id": collection_id})
        if not c:
            raise HTTPException(status_code=404, detail="Collection not found")
        update_data = {}
        if data.title is not None:
            update_data["title"] = data.title
        if data.slug is not None:
            update_data["slug"] = data.slug
        if data.description is not None:
            update_data["description"] = data.description
        if data.image is not None:
            update_data["image"] = data.image
        if data.is_active is not None:
            update_data["isActive"] = data.is_active
        c = await prisma.collection.update(where={"id": collection_id}, data=update_data)
        return CollectionOutput.from_prisma(c)

    async def delete(self, collection_id: int, email: str = Depends(verify_auth)) -> dict:
        c = await prisma.collection.find_unique(where={"id": collection_id})
        if not c:
            raise HTTPException(status_code=404, detail="Collection not found")
        await prisma.collectionproduct.delete_many(where={"collectionId": collection_id})
        await prisma.collection.delete(where={"id": collection_id})
        return {"success": True}

    async def add_product(self, collection_id: int, data: CollectionProductAddInput, email: str = Depends(verify_auth)) -> dict:
        c = await prisma.collection.find_unique(where={"id": collection_id})
        if not c:
            raise HTTPException(status_code=404, detail="Collection not found")
        p = await prisma.product.find_unique(where={"id": data.product_id})
        if not p:
            raise HTTPException(status_code=404, detail="Product not found")
        # determine position
        pos = data.position
        if pos == 0:
            count = await prisma.collectionproduct.count(where={"collectionId": collection_id})
            pos = count
        await prisma.collectionproduct.upsert(
            where={"collectionId_productId": {"collectionId": collection_id, "productId": data.product_id}},
            create={"collectionId": collection_id, "productId": data.product_id, "position": pos},
            update={"position": pos}
        )
        return {"success": True}

    async def remove_product(self, collection_id: int, product_id: int, email: str = Depends(verify_auth)) -> dict:
        await prisma.collectionproduct.delete_many(where={"collectionId": collection_id, "productId": product_id})
        return {"success": True}

    async def reorder_products(self, collection_id: int, data: CollectionProductReorderInput, email: str = Depends(verify_auth)) -> dict:
        for index, pid in enumerate(data.product_ids):
            await prisma.collectionproduct.update_many(
                where={"collectionId": collection_id, "productId": pid},
                data={"position": index}
            )
        return {"success": True}


