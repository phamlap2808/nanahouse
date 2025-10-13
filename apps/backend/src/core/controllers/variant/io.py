from typing import Optional, List
from pydantic import BaseModel, Field


class ProductOptionValueInput(BaseModel):
    value: str = Field(..., min_length=1)
    position: int = 0


class ProductOptionCreateInput(BaseModel):
    name: str = Field(..., min_length=1)
    position: int = 0
    values: List[ProductOptionValueInput] = []


class ProductOptionUpdateInput(BaseModel):
    name: Optional[str] = None
    position: Optional[int] = None
    values: Optional[List[ProductOptionValueInput]] = None


class ProductOptionOutput(BaseModel):
    id: int
    name: str
    position: int
    values: List[dict] = []

    @classmethod
    def from_prisma(cls, opt):
        return cls(
            id=opt.id,
            name=opt.name,
            position=opt.position,
            values=[{"id": v.id, "value": v.value, "position": v.position} for v in (opt.values or [])]
        )


class VariantOptionValueInput(BaseModel):
    option_id: int
    option_value_id: int


class ProductVariantCreateInput(BaseModel):
    sku: Optional[str] = None
    price: float
    compare_price: Optional[float] = None
    stock: int = 0
    track_stock: bool = True
    allow_backorder: bool = False
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    status: str = "active"
    barcode: Optional[str] = None
    image: Optional[str] = None
    options: List[VariantOptionValueInput] = []


class ProductVariantUpdateInput(BaseModel):
    sku: Optional[str] = None
    price: Optional[float] = None
    compare_price: Optional[float] = None
    stock: Optional[int] = None
    track_stock: Optional[bool] = None
    allow_backorder: Optional[bool] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    status: Optional[str] = None
    barcode: Optional[str] = None
    image: Optional[str] = None
    options: Optional[List[VariantOptionValueInput]] = None


class ProductVariantOutput(BaseModel):
    id: int
    sku: Optional[str]
    price: float
    compare_price: Optional[float]
    stock: int
    track_stock: bool
    allow_backorder: bool
    weight: Optional[float]
    dimensions: Optional[str]
    status: str
    barcode: Optional[str]
    image: Optional[str]
    options: List[dict] = []

    @classmethod
    def from_prisma(cls, v):
        opts = []
        if hasattr(v, 'optionValues') and v.optionValues:
            for ov in v.optionValues:
                opts.append({
                    "option_id": ov.optionId,
                    "option_value_id": ov.optionValueId,
                })
        return cls(
            id=v.id,
            sku=v.sku,
            price=v.price,
            compare_price=v.comparePrice,
            stock=v.stock,
            track_stock=v.trackStock,
            allow_backorder=v.allowBackorder,
            weight=v.weight,
            dimensions=v.dimensions,
            status=v.status,
            barcode=v.barcode,
            image=v.image,
            options=opts,
        )


