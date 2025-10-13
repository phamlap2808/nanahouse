from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class CartItemCreateInput(BaseModel):
    product_id: int = Field(..., description="Product ID to add to cart")
    quantity: int = Field(1, ge=1, description="Quantity to add")
    guest_token: Optional[str] = Field(None, description="Guest cart token (public)")


class CartItemUpdateInput(BaseModel):
    quantity: int = Field(..., ge=0, description="New quantity (0 to remove)")
    guest_token: Optional[str] = Field(None, description="Guest cart token (public)")


class CartItemOutput(BaseModel):
    id: int
    product_id: int
    quantity: int
    product_name: str
    product_price: float
    product_image: Optional[str] = None
    subtotal: float

    @classmethod
    def from_prisma(cls, cart_item):
        return cls(
            id=cart_item.id,
            product_id=cart_item.productId,
            quantity=cart_item.quantity,
            product_name=cart_item.product.name,
            product_price=cart_item.product.price,
            product_image=getattr(cart_item.product, 'image', None),
            subtotal=cart_item.quantity * cart_item.product.price
        )


class CartOutput(BaseModel):
    id: int
    user_id: Optional[int] = None
    guest_token: Optional[str] = None
    items: List[CartItemOutput] = []
    total_items: int = 0
    subtotal: float = 0.0
    discount_amount: float = 0.0
    shipping: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    applied_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_prisma(cls, cart):
        items = [CartItemOutput.from_prisma(item) for item in cart.items] if cart.items else []
        total_items = sum(item.quantity for item in items)
        subtotal = sum(item.subtotal for item in items)
        discount_amount = 0.0
        shipping = 0.0
        tax = 0.0
        total = subtotal - discount_amount + shipping + tax
        applied_code = None
        if hasattr(cart, 'appliedDiscountCode') and cart.appliedDiscountCode:
            applied_code = cart.appliedDiscountCode.code
        
        return cls(
            id=cart.id,
            user_id=cart.userId,
            guest_token=getattr(cart, 'guestToken', None),
            items=items,
            total_items=total_items,
            subtotal=subtotal,
            discount_amount=discount_amount,
            shipping=shipping,
            tax=tax,
            total=total,
            applied_code=applied_code,
            created_at=cart.createdAt,
            updated_at=cart.updatedAt
        )


class CartListInput(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(10, ge=1, le=100, description="Items per page")


class CartItemListInput(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(10, ge=1, le=100, description="Items per page")
