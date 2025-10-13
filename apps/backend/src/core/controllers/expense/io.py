from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class ExpenseCategoryCreateInput(BaseModel):
    name: str = Field(..., min_length=1)
    color: Optional[str] = None


class ExpenseCategoryUpdateInput(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    color: Optional[str] = None


class ExpenseCategoryOutput(BaseModel):
    id: int
    name: str
    color: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_prisma(cls, cat):
        return cls(
            id=cat.id,
            name=cat.name,
            color=cat.color,
            created_at=cat.createdAt,
            updated_at=cat.updatedAt,
        )


class ExpenseCreateInput(BaseModel):
    category_id: int
    amount: float = Field(..., gt=0)
    currency: str = Field("VND")
    description: Optional[str] = None
    occurred_at: Optional[datetime] = None


class ExpenseUpdateInput(BaseModel):
    category_id: Optional[int] = None
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = None
    description: Optional[str] = None
    occurred_at: Optional[datetime] = None


class ExpenseOutput(BaseModel):
    id: int
    category: ExpenseCategoryOutput
    amount: float
    currency: str
    description: Optional[str] = None
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_prisma(cls, exp):
        return cls(
            id=exp.id,
            category=ExpenseCategoryOutput.from_prisma(exp.category) if hasattr(exp, 'category') else None,
            amount=exp.amount,
            currency=exp.currency,
            description=exp.description,
            occurred_at=exp.occurredAt,
            created_at=exp.createdAt,
            updated_at=exp.updatedAt,
        )


class ExpenseListInput(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    category_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


