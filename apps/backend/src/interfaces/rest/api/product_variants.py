from dataclasses import dataclass
from fastapi import APIRouter
from interfaces.rest.utils import APIRoute, add_api_route
from core.controllers.variant import ProductVariantController
from core.controllers.variant.io import (
    ProductOptionCreateInput, ProductOptionUpdateInput, ProductOptionOutput,
    ProductVariantCreateInput, ProductVariantUpdateInput, ProductVariantOutput,
)


@dataclass(kw_only=True)
class ProductOptionsRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/products/{product_id}/options", tags=["Product Variants"])
        ctrl = ProductVariantController()
        add_api_route(self.router, [
            APIRoute(path="/", methods=["GET"], handler=ctrl.list_options, response_model=list[ProductOptionOutput]),
            APIRoute(path="/", methods=["POST"], handler=ctrl.create_option, response_model=ProductOptionOutput),
            APIRoute(path="/{option_id}", methods=["PUT"], handler=ctrl.update_option, response_model=ProductOptionOutput),
            APIRoute(path="/{option_id}", methods=["DELETE"], handler=ctrl.delete_option),
        ])


@dataclass(kw_only=True)
class ProductVariantsRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/products/{product_id}/variants", tags=["Product Variants"])
        ctrl = ProductVariantController()
        add_api_route(self.router, [
            APIRoute(path="/", methods=["GET"], handler=ctrl.list_variants, response_model=list[ProductVariantOutput]),
            APIRoute(path="/", methods=["POST"], handler=ctrl.create_variant, response_model=ProductVariantOutput),
            APIRoute(path="/{variant_id}", methods=["PUT"], handler=ctrl.update_variant, response_model=ProductVariantOutput),
            APIRoute(path="/{variant_id}", methods=["DELETE"], handler=ctrl.delete_variant),
        ])


