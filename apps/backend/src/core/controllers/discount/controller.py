from fastapi import HTTPException, Depends
from prisma import Prisma
from core.auth_utils import verify_auth
from .io import (
    DiscountCreateInput, DiscountUpdateInput, DiscountOutput,
    DiscountCodeInput
)

prisma = Prisma()


class DiscountController:
    async def list(self, email: str = Depends(verify_auth)) -> list[DiscountOutput]:
        discounts = await prisma.discount.find_many(include={"codes": True}, order={"createdAt": "desc"})
        return [DiscountOutput.from_prisma(d) for d in discounts]

    async def create(self, data: DiscountCreateInput, email: str = Depends(verify_auth)) -> DiscountOutput:
        d = await prisma.discount.create(
            data={
                "name": data.name,
                "type": data.type,
                "value": data.value,
                "isActive": data.is_active,
                "startsAt": data.starts_at,
                "endsAt": data.ends_at,
                "totalUsageLimit": data.total_usage_limit,
                "usesPerCustomer": data.uses_per_customer,
                "codes": {"create": [
                    {
                        "code": c.code,
                        "usageLimit": c.usage_limit,
                        "startsAt": c.starts_at,
                        "endsAt": c.ends_at,
                        "isActive": c.is_active,
                    } for c in data.codes
                ]} if data.codes else {},
                "conditions": {"create": {
                    "minSubtotal": data.condition.min_subtotal if data.condition else None,
                    "minItems": data.condition.min_items if data.condition else None,
                    "appliesOnce": data.condition.applies_once if data.condition else None,
                    "bogoBuyQty": data.condition.bogo_buy_qty if data.condition else None,
                    "bogoGetQty": data.condition.bogo_get_qty if data.condition else None,
                    "bogoGetPercent": data.condition.bogo_get_percent if data.condition else None,
                    "freeShipping": data.condition.free_shipping if data.condition else None,
                }} if data.condition else {},
            },
            include={"codes": True}
        )
        return DiscountOutput.from_prisma(d)

    async def get(self, discount_id: int, email: str = Depends(verify_auth)) -> DiscountOutput:
        d = await prisma.discount.find_unique(where={"id": discount_id}, include={"codes": True, "conditions": True})
        if not d:
            raise HTTPException(status_code=404, detail="Discount not found")
        return DiscountOutput.from_prisma(d)

    async def update(self, discount_id: int, data: DiscountUpdateInput, email: str = Depends(verify_auth)) -> DiscountOutput:
        disc = await prisma.discount.find_unique(where={"id": discount_id})
        if not disc:
            raise HTTPException(status_code=404, detail="Discount not found")

        update_data = {}
        if data.name is not None:
            update_data["name"] = data.name
        if data.type is not None:
            update_data["type"] = data.type
        if data.value is not None:
            update_data["value"] = data.value
        if data.is_active is not None:
            update_data["isActive"] = data.is_active
        if data.starts_at is not None:
            update_data["startsAt"] = data.starts_at
        if data.ends_at is not None:
            update_data["endsAt"] = data.ends_at
        if data.total_usage_limit is not None:
            update_data["totalUsageLimit"] = data.total_usage_limit
        if data.uses_per_customer is not None:
            update_data["usesPerCustomer"] = data.uses_per_customer

        d = await prisma.discount.update(where={"id": discount_id}, data=update_data)

        # Replace codes if provided
        if data.codes is not None:
            await prisma.discountcode.delete_many(where={"discountId": discount_id})
            if data.codes:
                await prisma.discountcode.create_many(data=[{
                    "discountId": discount_id,
                    "code": c.code,
                    "usageLimit": c.usage_limit,
                    "startsAt": c.starts_at,
                    "endsAt": c.ends_at,
                    "isActive": c.is_active,
                } for c in data.codes])

        # Replace condition if provided
        if data.condition is not None:
            await prisma.discountcondition.delete_many(where={"discountId": discount_id})
            if data.condition:
                c = data.condition
                await prisma.discountcondition.create(data={
                    "discountId": discount_id,
                    "minSubtotal": c.min_subtotal,
                    "minItems": c.min_items,
                    "appliesOnce": c.applies_once,
                    "bogoBuyQty": c.bogo_buy_qty,
                    "bogoGetQty": c.bogo_get_qty,
                    "bogoGetPercent": c.bogo_get_percent,
                    "freeShipping": c.free_shipping,
                })

        d = await prisma.discount.find_unique(where={"id": discount_id}, include={"codes": True})
        return DiscountOutput.from_prisma(d)

    async def delete(self, discount_id: int, email: str = Depends(verify_auth)) -> dict:
        await prisma.discountcode.delete_many(where={"discountId": discount_id})
        await prisma.discountcondition.delete_many(where={"discountId": discount_id})
        await prisma.discountproduct.delete_many(where={"discountId": discount_id})
        await prisma.discountcollection.delete_many(where={"discountId": discount_id})
        await prisma.discount.delete(where={"id": discount_id})
        return {"success": True}

    async def activate(self, discount_id: int, email: str = Depends(verify_auth)) -> dict:
        await prisma.discount.update(where={"id": discount_id}, data={"isActive": True})
        return {"success": True}

    async def deactivate(self, discount_id: int, email: str = Depends(verify_auth)) -> dict:
        await prisma.discount.update(where={"id": discount_id}, data={"isActive": False})
        return {"success": True}


