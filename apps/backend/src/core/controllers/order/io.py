from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class OrderCreateInput(BaseModel):
    # Shipping info
    shipping_name: str = Field(..., description="Shipping recipient name")
    shipping_phone: str = Field(..., description="Shipping phone number")
    shipping_address: str = Field(..., description="Shipping address")
    shipping_city: str = Field(..., description="Shipping city")
    shipping_state: Optional[str] = Field(None, description="Shipping state/province")
    shipping_zip: Optional[str] = Field(None, description="Shipping postal code")
    shipping_country: str = Field("Vietnam", description="Shipping country")
    
    # Order details
    notes: Optional[str] = Field(None, description="Order notes")
    discount: float = Field(0, ge=0, description="Discount amount")


class OrderUpdateInput(BaseModel):
    status: Optional[str] = Field(None, description="Order status")
    shipping_name: Optional[str] = Field(None, description="Shipping recipient name")
    shipping_phone: Optional[str] = Field(None, description="Shipping phone number")
    shipping_address: Optional[str] = Field(None, description="Shipping address")
    shipping_city: Optional[str] = Field(None, description="Shipping city")
    shipping_state: Optional[str] = Field(None, description="Shipping state/province")
    shipping_zip: Optional[str] = Field(None, description="Shipping postal code")
    shipping_country: Optional[str] = Field(None, description="Shipping country")
    notes: Optional[str] = Field(None, description="Order notes")


class OrderItemOutput(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    name: str
    sku: Optional[str] = None
    subtotal: float

    @classmethod
    def from_prisma(cls, order_item):
        return cls(
            id=order_item.id,
            product_id=order_item.productId,
            quantity=order_item.quantity,
            price=order_item.price,
            name=order_item.name,
            sku=order_item.sku,
            subtotal=order_item.quantity * order_item.price
        )


class PaymentOutput(BaseModel):
    id: int
    amount: float
    currency: str
    method: str
    status: str
    transaction_id: Optional[str] = None
    gateway: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime

    @classmethod
    def from_prisma(cls, payment):
        return cls(
            id=payment.id,
            amount=payment.amount,
            currency=payment.currency,
            method=payment.method,
            status=payment.status,
            transaction_id=payment.transactionId,
            gateway=payment.gateway,
            paid_at=payment.paidAt,
            created_at=payment.createdAt
        )


class OrderOutput(BaseModel):
    id: int
    order_number: str
    user_id: int
    status: str
    subtotal: float
    tax: float
    shipping: float
    discount: float
    total: float
    
    # Shipping info
    shipping_name: Optional[str] = None
    shipping_phone: Optional[str] = None
    shipping_address: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_zip: Optional[str] = None
    shipping_country: Optional[str] = None
    
    # Order items and payments
    items: List[OrderItemOutput] = []
    payments: List[PaymentOutput] = []
    
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_prisma(cls, order):
        return cls(
            id=order.id,
            order_number=order.orderNumber,
            user_id=order.userId,
            status=order.status,
            subtotal=order.subtotal,
            tax=order.tax,
            shipping=order.shipping,
            discount=order.discount,
            total=order.total,
            shipping_name=order.shippingName,
            shipping_phone=order.shippingPhone,
            shipping_address=order.shippingAddress,
            shipping_city=order.shippingCity,
            shipping_state=order.shippingState,
            shipping_zip=order.shippingZip,
            shipping_country=order.shippingCountry,
            items=[OrderItemOutput.from_prisma(item) for item in order.items] if order.items else [],
            payments=[PaymentOutput.from_prisma(payment) for payment in order.payments] if order.payments else [],
            notes=order.notes,
            created_at=order.createdAt,
            updated_at=order.updatedAt
        )


class OrderListInput(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(10, ge=1, le=100, description="Items per page")
    status: Optional[str] = Field(None, description="Filter by status")


class PaymentCreateInput(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount")
    method: str = Field(..., description="Payment method")
    gateway: Optional[str] = Field(None, description="Payment gateway")
    transaction_id: Optional[str] = Field(None, description="External transaction ID")


class PaymentUpdateInput(BaseModel):
    status: str = Field(..., description="Payment status")
    transaction_id: Optional[str] = Field(None, description="External transaction ID")
    gateway_data: Optional[str] = Field(None, description="Gateway response data")
