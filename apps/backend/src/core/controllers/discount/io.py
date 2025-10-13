from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class DiscountConditionInput(BaseModel):
    min_subtotal: Optional[float] = None
    min_items: Optional[int] = None
    applies_once: Optional[bool] = None
    bogo_buy_qty: Optional[int] = None
    bogo_get_qty: Optional[int] = None
    bogo_get_percent: Optional[float] = None
    free_shipping: Optional[bool] = None


class DiscountCodeInput(BaseModel):
    code: str = Field(..., min_length=1)
    usage_limit: Optional[int] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    is_active: bool = True


class DiscountCreateInput(BaseModel):
    name: str
    type: str  # percentage, fixed_amount, free_shipping, bogo
    value: Optional[float] = None
    is_active: bool = True
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    total_usage_limit: Optional[int] = None
    uses_per_customer: Optional[int] = 1
    codes: List[DiscountCodeInput] = []
    condition: Optional[DiscountConditionInput] = None


class DiscountUpdateInput(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[float] = None
    is_active: Optional[bool] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    total_usage_limit: Optional[int] = None
    uses_per_customer: Optional[int] = None
    codes: Optional[List[DiscountCodeInput]] = None
    condition: Optional[DiscountConditionInput] = None


class DiscountCodeOutput(BaseModel):
    id: int
    code: str
    usage_limit: Optional[int]
    used_count: int
    starts_at: Optional[datetime]
    ends_at: Optional[datetime]
    is_active: bool

    @classmethod
    def from_prisma(cls, c):
        return cls(
            id=c.id,
            code=c.code,
            usage_limit=c.usageLimit,
            used_count=c.usedCount,
            starts_at=c.startsAt,
            ends_at=c.endsAt,
            is_active=c.isActive,
        )


class DiscountOutput(BaseModel):
    id: int
    name: str
    type: str
    value: Optional[float]
    is_active: bool
    starts_at: Optional[datetime]
    ends_at: Optional[datetime]
    total_usage_limit: Optional[int]
    uses_per_customer: Optional[int]
    codes: List[DiscountCodeOutput] = []

    @classmethod
    def from_prisma(cls, d):
        return cls(
            id=d.id,
            name=d.name,
            type=d.type,
            value=d.value,
            is_active=d.isActive,
            starts_at=d.startsAt,
            ends_at=d.endsAt,
            total_usage_limit=d.totalUsageLimit,
            uses_per_customer=d.usesPerCustomer,
            codes=[DiscountCodeOutput.from_prisma(c) for c in (d.codes or [])]
        )


