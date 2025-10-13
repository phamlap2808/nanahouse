from fastapi import HTTPException, Depends
from prisma import Prisma
from core.auth_utils import verify_auth
from .io import (
    ProductOptionCreateInput, ProductOptionUpdateInput, ProductOptionOutput,
    ProductVariantCreateInput, ProductVariantUpdateInput, ProductVariantOutput,
)

prisma = Prisma()


class ProductVariantController:
    # Options
    async def list_options(self, product_id: int, email: str = Depends(verify_auth)) -> list[ProductOptionOutput]:
        product = await prisma.product.find_unique(where={"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        options = await prisma.productoption.find_many(
            where={"productId": product_id},
            include={"values": True},
            order={"position": "asc"}
        )
        return [ProductOptionOutput.from_prisma(o) for o in options]

    async def create_option(self, product_id: int, data: ProductOptionCreateInput, email: str = Depends(verify_auth)) -> ProductOptionOutput:
        product = await prisma.product.find_unique(where={"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        option = await prisma.productoption.create(
            data={
                "productId": product_id,
                "name": data.name,
                "position": data.position,
                "values": {"create": [{"value": v.value, "position": v.position} for v in data.values]}
            },
            include={"values": True}
        )
        return ProductOptionOutput.from_prisma(option)

    async def update_option(self, product_id: int, option_id: int, data: ProductOptionUpdateInput, email: str = Depends(verify_auth)) -> ProductOptionOutput:
        opt = await prisma.productoption.find_first(where={"id": option_id, "productId": product_id}, include={"values": True})
        if not opt:
            raise HTTPException(status_code=404, detail="Option not found")

        update_data = {}
        if data.name is not None:
            update_data["name"] = data.name
        if data.position is not None:
            update_data["position"] = data.position

        option = await prisma.productoption.update(where={"id": option_id}, data=update_data, include={"values": True})

        # Sync values if provided: simple replace
        if data.values is not None:
            await prisma.productoptionvalue.delete_many(where={"optionId": option_id})
            if data.values:
                await prisma.productoptionvalue.create_many(data=[{"optionId": option_id, "value": v.value, "position": v.position} for v in data.values])
            option = await prisma.productoption.find_unique(where={"id": option_id}, include={"values": True})

        return ProductOptionOutput.from_prisma(option)

    async def delete_option(self, product_id: int, option_id: int, email: str = Depends(verify_auth)) -> dict:
        opt = await prisma.productoption.find_first(where={"id": option_id, "productId": product_id})
        if not opt:
            raise HTTPException(status_code=404, detail="Option not found")
        # Remove dependent variant option links
        await prisma.productvariantoptionvalue.delete_many(where={"optionId": option_id})
        await prisma.productoptionvalue.delete_many(where={"optionId": option_id})
        await prisma.productoption.delete(where={"id": option_id})
        return {"success": True}

    # Variants
    async def list_variants(self, product_id: int, email: str = Depends(verify_auth)) -> list[ProductVariantOutput]:
        product = await prisma.product.find_unique(where={"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        variants = await prisma.productvariant.find_many(
            where={"productId": product_id},
            include={"optionValues": True},
            order={"id": "asc"}
        )
        return [ProductVariantOutput.from_prisma(v) for v in variants]

    async def create_variant(self, product_id: int, data: ProductVariantCreateInput, email: str = Depends(verify_auth)) -> ProductVariantOutput:
        product = await prisma.product.find_unique(where={"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        variant = await prisma.productvariant.create(
            data={
                "productId": product_id,
                "sku": data.sku,
                "price": data.price,
                "comparePrice": data.compare_price,
                "stock": data.stock,
                "trackStock": data.track_stock,
                "allowBackorder": data.allow_backorder,
                "weight": data.weight,
                "dimensions": data.dimensions,
                "status": data.status,
                "barcode": data.barcode,
                "image": data.image,
                "optionValues": {
                    "create": [
                        {"optionId": ov.option_id, "optionValueId": ov.option_value_id}
                        for ov in data.options
                    ]
                }
            },
            include={"optionValues": True}
        )
        return ProductVariantOutput.from_prisma(variant)

    async def update_variant(self, product_id: int, variant_id: int, data: ProductVariantUpdateInput, email: str = Depends(verify_auth)) -> ProductVariantOutput:
        var = await prisma.productvariant.find_first(where={"id": variant_id, "productId": product_id})
        if not var:
            raise HTTPException(status_code=404, detail="Variant not found")

        update_data = {}
        if data.sku is not None:
            update_data["sku"] = data.sku
        if data.price is not None:
            update_data["price"] = data.price
        if data.compare_price is not None:
            update_data["comparePrice"] = data.compare_price
        if data.stock is not None:
            update_data["stock"] = data.stock
        if data.track_stock is not None:
            update_data["trackStock"] = data.track_stock
        if data.allow_backorder is not None:
            update_data["allowBackorder"] = data.allow_backorder
        if data.weight is not None:
            update_data["weight"] = data.weight
        if data.dimensions is not None:
            update_data["dimensions"] = data.dimensions
        if data.status is not None:
            update_data["status"] = data.status
        if data.barcode is not None:
            update_data["barcode"] = data.barcode
        if data.image is not None:
            update_data["image"] = data.image

        variant = await prisma.productvariant.update(where={"id": variant_id}, data=update_data, include={"optionValues": True})

        if data.options is not None:
            await prisma.productvariantoptionvalue.delete_many(where={"variantId": variant_id})
            if data.options:
                await prisma.productvariantoptionvalue.create_many(
                    data=[{"variantId": variant_id, "optionId": ov.option_id, "optionValueId": ov.option_value_id} for ov in data.options]
                )
            variant = await prisma.productvariant.find_unique(where={"id": variant_id}, include={"optionValues": True})

        return ProductVariantOutput.from_prisma(variant)

    async def delete_variant(self, product_id: int, variant_id: int, email: str = Depends(verify_auth)) -> dict:
        var = await prisma.productvariant.find_first(where={"id": variant_id, "productId": product_id})
        if not var:
            raise HTTPException(status_code=404, detail="Variant not found")
        await prisma.productvariantoptionvalue.delete_many(where={"variantId": variant_id})
        await prisma.productvariant.delete(where={"id": variant_id})
        return {"success": True}


