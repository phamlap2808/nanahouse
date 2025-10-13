from typing import Optional, List
from fastapi import HTTPException, Depends
from prisma import Prisma
from core.auth_utils import verify_auth
import secrets
from .io import (
    CartItemCreateInput,
    CartItemUpdateInput,
    CartOutput,
    CartListInput,
    CartItemListInput
)

prisma = Prisma()


class CartController:
    # Public guest cart
    async def public_get_or_create(self, guest_token: str | None = None) -> CartOutput:
        if guest_token:
            cart = await prisma.cart.find_unique(where={"guestToken": guest_token}, include={"items": {"include": {"product": True}}, "appliedDiscountCode": True})
            if cart:
                return CartOutput.from_prisma(cart)
        # create new guest cart
        token = secrets.token_urlsafe(24)
        cart = await prisma.cart.create(data={"guestToken": token})
        cart = await prisma.cart.find_unique(where={"id": cart.id}, include={"items": {"include": {"product": True}}, "appliedDiscountCode": True})
        out = CartOutput.from_prisma(cart)
        out.guest_token = token
        return out

    async def public_add_item(self, data: CartItemCreateInput) -> CartOutput:
        # find or create cart by guest token
        if not data.guest_token:
            # create new cart and then add
            cart_out = await self.public_get_or_create(None)
            guest_token = cart_out.guest_token
        else:
            guest_token = data.guest_token
            cart_out = await self.public_get_or_create(guest_token)
        cart = await prisma.cart.find_unique(where={"guestToken": guest_token})
        # product
        product = await prisma.product.find_first(where={"id": data.product_id, "status": "active"})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found or not active")
        # existing item
        existing_item = await prisma.cartitem.find_first(where={"cartId": cart.id, "productId": data.product_id})
        if existing_item:
            new_quantity = existing_item.quantity + data.quantity
            if product.trackStock and product.stock < new_quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")
            await prisma.cartitem.update(where={"id": existing_item.id}, data={"quantity": new_quantity})
        else:
            await prisma.cartitem.create(data={"cartId": cart.id, "productId": data.product_id, "quantity": data.quantity})
        updated = await prisma.cart.find_unique(where={"id": cart.id}, include={"items": {"include": {"product": True}}, "appliedDiscountCode": True})
        out = CartOutput.from_prisma(updated)
        out.guest_token = guest_token
        return out

    async def public_update_item(self, item_id: int, data: CartItemUpdateInput) -> CartOutput:
        if not data.guest_token:
            raise HTTPException(status_code=400, detail="guest_token required")
        cart = await prisma.cart.find_unique(where={"guestToken": data.guest_token})
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        item = await prisma.cartitem.find_first(where={"id": item_id, "cartId": cart.id}, include={"product": True})
        if not item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        if data.quantity == 0:
            await prisma.cartitem.delete(where={"id": item_id})
        else:
            if item.product.trackStock and item.product.stock < data.quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")
            await prisma.cartitem.update(where={"id": item_id}, data={"quantity": data.quantity})
        updated = await prisma.cart.find_unique(where={"id": cart.id}, include={"items": {"include": {"product": True}}, "appliedDiscountCode": True})
        out = CartOutput.from_prisma(updated)
        out.guest_token = data.guest_token
        return out

    async def public_clear(self, guest_token: str) -> CartOutput:
        cart = await prisma.cart.find_unique(where={"guestToken": guest_token})
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        await prisma.cartitem.delete_many(where={"cartId": cart.id})
        updated = await prisma.cart.find_unique(where={"id": cart.id}, include={"items": {"include": {"product": True}}, "appliedDiscountCode": True})
        out = CartOutput.from_prisma(updated)
        out.guest_token = guest_token
        return out

    async def public_apply_discount(self, code: str, guest_token: str) -> CartOutput:
        cart = await prisma.cart.find_unique(where={"guestToken": guest_token}, include={"items": {"include": {"product": True}}, "appliedDiscountCode": True})
        if not cart or (not cart.items):
            raise HTTPException(status_code=400, detail="Cart is empty")
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        code_row = await prisma.discountcode.find_first(
            where={
                "code": code,
                "isActive": True,
                "startsAt": {"lte": now},
                "OR": [{"endsAt": None}, {"endsAt": {"gte": now}}]
            },
            include={"discount": {"include": {"conditions": True}}}
        )
        if not code_row:
            raise HTTPException(status_code=404, detail="Discount code not found or inactive")
        await prisma.cart.update(where={"id": cart.id}, data={"appliedDiscountCodeId": code_row.id})
        updated = await prisma.cart.find_unique(where={"id": cart.id}, include={"items": {"include": {"product": True}}, "appliedDiscountCode": True})
        out = CartOutput.from_prisma(updated)
        out.guest_token = guest_token
        return out

    async def public_remove_discount(self, guest_token: str) -> CartOutput:
        cart = await prisma.cart.find_unique(where={"guestToken": guest_token}, include={"items": {"include": {"product": True}}, "appliedDiscountCode": True})
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        await prisma.cart.update(where={"id": cart.id}, data={"appliedDiscountCodeId": None})
        updated = await prisma.cart.find_unique(where={"id": cart.id}, include={"items": {"include": {"product": True}}, "appliedDiscountCode": True})
        out = CartOutput.from_prisma(updated)
        out.guest_token = guest_token
        return out
    async def get_cart(self, email: str = Depends(verify_auth)) -> CartOutput:
        """Get user's cart"""
        # Get user
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get or create cart
        cart = await prisma.cart.find_unique(
            where={"userId": user.id},
            include={"items": {"include": {"product": True}}, "appliedDiscountCode": True}
        )
        
        if not cart:
            # Create empty cart
            cart = await prisma.cart.create(
                data={"userId": user.id},
                include={"items": {"include": {"product": True}}, "appliedDiscountCode": True}
            )

        return CartOutput.from_prisma(cart)

    async def add_item(self, data: CartItemCreateInput, email: str = Depends(verify_auth)) -> CartOutput:
        """Add item to cart"""
        # Get user
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check product exists and is active
        product = await prisma.product.find_first(
            where={
                "id": data.product_id,
                "status": "active"
            }
        )
        if not product:
            raise HTTPException(status_code=404, detail="Product not found or not active")

        # Check stock
        if product.trackStock and product.stock < data.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")

        # Get or create cart
        cart = await prisma.cart.find_unique(where={"userId": user.id})
        if not cart:
            cart = await prisma.cart.create(data={"userId": user.id})

        # Check if item already exists in cart
        existing_item = await prisma.cartitem.find_unique(
            where={
                "cartId_productId": {
                    "cartId": cart.id,
                    "productId": data.product_id
                }
            }
        )

        if existing_item:
            # Update quantity
            new_quantity = existing_item.quantity + data.quantity
            if product.trackStock and product.stock < new_quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")
            
            await prisma.cartitem.update(
                where={"id": existing_item.id},
                data={"quantity": new_quantity}
            )
        else:
            # Add new item
            await prisma.cartitem.create(
                data={
                    "cartId": cart.id,
                    "productId": data.product_id,
                    "quantity": data.quantity
                }
            )

        # Return updated cart
        updated_cart = await prisma.cart.find_unique(
            where={"id": cart.id},
            include={"items": {"include": {"product": True}}, "appliedDiscountCode": True}
        )
        return CartOutput.from_prisma(updated_cart)

    async def update_item(self, item_id: int, data: CartItemUpdateInput, email: str = Depends(verify_auth)) -> CartOutput:
        """Update cart item quantity"""
        # Get user
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get cart item
        cart_item = await prisma.cartitem.find_first(
            where={
                "id": item_id,
                "cart": {"userId": user.id}
            },
            include={"product": True}
        )
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")

        if data.quantity == 0:
            # Remove item
            await prisma.cartitem.delete(where={"id": item_id})
        else:
            # Check stock
            if cart_item.product.trackStock and cart_item.product.stock < data.quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")
            
            # Update quantity
            await prisma.cartitem.update(
                where={"id": item_id},
                data={"quantity": data.quantity}
            )

        # Return updated cart
        cart = await prisma.cart.find_unique(
            where={"userId": user.id},
            include={"items": {"include": {"product": True}}, "appliedDiscountCode": True}
        )
        return CartOutput.from_prisma(cart)

    async def remove_item(self, item_id: int, email: str = Depends(verify_auth)) -> CartOutput:
        """Remove item from cart"""
        # Get user
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if item exists and belongs to user
        cart_item = await prisma.cartitem.find_first(
            where={
                "id": item_id,
                "cart": {"userId": user.id}
            }
        )
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")

        # Remove item
        await prisma.cartitem.delete(where={"id": item_id})

        # Return updated cart
        cart = await prisma.cart.find_unique(
            where={"userId": user.id},
            include={"items": {"include": {"product": True}}}
        )
        return CartOutput.from_prisma(cart)

    async def clear_cart(self, email: str = Depends(verify_auth)) -> CartOutput:
        """Clear all items from cart"""
        # Get user
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get cart
        cart = await prisma.cart.find_unique(where={"userId": user.id})
        if not cart:
            # Create empty cart
            cart = await prisma.cart.create(data={"userId": user.id})
        else:
            # Clear all items
            await prisma.cartitem.delete_many(where={"cartId": cart.id})

        # Return empty cart
        updated_cart = await prisma.cart.find_unique(
            where={"id": cart.id},
            include={"items": {"include": {"product": True}}, "appliedDiscountCode": True}
        )
        return CartOutput.from_prisma(updated_cart)

    async def get_cart_count(self, email: str = Depends(verify_auth)) -> dict:
        """Get cart items count"""
        # Get user
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get cart
        cart = await prisma.cart.find_unique(
            where={"userId": user.id},
            include={"items": True}
        )
        
        if not cart:
            return {"count": 0}

        total_items = sum(item.quantity for item in cart.items)
        return {"count": total_items}

    async def apply_discount(self, code: str, email: str = Depends(verify_auth)) -> CartOutput:
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        cart = await prisma.cart.find_unique(
            where={"userId": user.id},
            include={"items": {"include": {"product": True}}, "appliedDiscountCode": True}
        )
        if not cart or not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        # find active code
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        code_row = await prisma.discountcode.find_first(
            where={
                "code": code,
                "isActive": True,
                "startsAt": {"lte": now},
                "OR": [{"endsAt": None}, {"endsAt": {"gte": now}}]
            },
            include={"discount": {"include": {"conditions": True}}}
        )
        if not code_row:
            raise HTTPException(status_code=404, detail="Discount code not found or inactive")

        # attach to cart
        await prisma.cart.update(
            where={"id": cart.id},
            data={"appliedDiscountCodeId": code_row.id}
        )
        cart = await prisma.cart.find_unique(
            where={"id": cart.id},
            include={"items": {"include": {"product": True}}, "appliedDiscountCode": True}
        )
        return CartOutput.from_prisma(cart)

    async def remove_discount(self, email: str = Depends(verify_auth)) -> CartOutput:
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        cart = await prisma.cart.find_unique(
            where={"userId": user.id},
            include={"items": {"include": {"product": True}}, "appliedDiscountCode": True}
        )
        if not cart:
            cart = await prisma.cart.create(data={"userId": user.id})
        else:
            await prisma.cart.update(where={"id": cart.id}, data={"appliedDiscountCodeId": None})
        cart = await prisma.cart.find_unique(
            where={"userId": user.id},
            include={"items": {"include": {"product": True}}, "appliedDiscountCode": True}
        )
        return CartOutput.from_prisma(cart)
