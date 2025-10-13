from fastapi import HTTPException, Depends
from prisma import Prisma
from core.auth_utils import verify_auth
from .io import (
    CategoryAttributeCreateInput, CategoryAttributeUpdateInput, CategoryAttributeOutput,
    ProductAttributeValueSetInput, ProductAttributeValueOutput
)

prisma = Prisma()


class AttributeController:
    # Category attributes
    async def list_category_attributes(self, category_id: int, email: str = Depends(verify_auth)) -> list[CategoryAttributeOutput]:
        cat = await prisma.category.find_unique(where={"id": category_id})
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")
        attrs = await prisma.categoryattribute.find_many(where={"categoryId": category_id}, order={"position": "asc"})
        return [CategoryAttributeOutput.from_prisma(a) for a in attrs]

    async def create_category_attribute(self, category_id: int, data: CategoryAttributeCreateInput, email: str = Depends(verify_auth)) -> CategoryAttributeOutput:
        cat = await prisma.category.find_unique(where={"id": category_id})
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")
        a = await prisma.categoryattribute.create(data={
            "categoryId": category_id,
            "name": data.name,
            "type": data.type,
            "options": data.options,
            "position": data.position,
        })
        return CategoryAttributeOutput.from_prisma(a)

    async def update_category_attribute(self, category_id: int, attribute_id: int, data: CategoryAttributeUpdateInput, email: str = Depends(verify_auth)) -> CategoryAttributeOutput:
        a = await prisma.categoryattribute.find_first(where={"id": attribute_id, "categoryId": category_id})
        if not a:
            raise HTTPException(status_code=404, detail="Attribute not found")
        update_data = {}
        if data.name is not None:
            update_data["name"] = data.name
        if data.type is not None:
            update_data["type"] = data.type
        if data.options is not None:
            update_data["options"] = data.options
        if data.position is not None:
            update_data["position"] = data.position
        a = await prisma.categoryattribute.update(where={"id": attribute_id}, data=update_data)
        return CategoryAttributeOutput.from_prisma(a)

    async def delete_category_attribute(self, category_id: int, attribute_id: int, email: str = Depends(verify_auth)) -> dict:
        a = await prisma.categoryattribute.find_first(where={"id": attribute_id, "categoryId": category_id})
        if not a:
            raise HTTPException(status_code=404, detail="Attribute not found")
        await prisma.productattributevalue.delete_many(where={"attributeId": attribute_id})
        await prisma.categoryattribute.delete(where={"id": attribute_id})
        return {"success": True}

    # Product attribute values
    async def list_product_attribute_values(self, product_id: int, email: str = Depends(verify_auth)) -> list[ProductAttributeValueOutput]:
        product = await prisma.product.find_unique(where={"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        values = await prisma.productattributevalue.find_many(where={"productId": product_id}, order={"attributeId": "asc"})
        return [{"attribute_id": v.attributeId, "value": v.value} for v in values]

    async def set_product_attribute_values(self, product_id: int, data: ProductAttributeValueSetInput, email: str = Depends(verify_auth)) -> dict:
        product = await prisma.product.find_unique(where={"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        # Upsert values
        for item in data.values:
            attr_id = item.get("attribute_id")
            val = item.get("value")
            if attr_id is None:
                continue
            await prisma.productattributevalue.upsert(
                where={"productId_attributeId": {"productId": product_id, "attributeId": attr_id}},
                create={"productId": product_id, "attributeId": attr_id, "value": val or ""},
                update={"value": val or ""}
            )
        return {"success": True}

    async def delete_product_attribute_value(self, product_id: int, attribute_id: int, email: str = Depends(verify_auth)) -> dict:
        await prisma.productattributevalue.delete_many(where={"productId": product_id, "attributeId": attribute_id})
        return {"success": True}


