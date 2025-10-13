from dataclasses import dataclass
from fastapi import APIRouter
from interfaces.rest.utils import APIRoute, add_api_route
from core.controllers.attribute import AttributeController
from core.controllers.attribute.io import (
    CategoryAttributeCreateInput, CategoryAttributeUpdateInput, CategoryAttributeOutput,
    ProductAttributeValueSetInput
)


@dataclass(kw_only=True)
class CategoryAttributesRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/categories/{category_id}/attributes", tags=["Attributes"])
        ctrl = AttributeController()
        add_api_route(self.router, [
            APIRoute(path="/", methods=["GET"], handler=ctrl.list_category_attributes, response_model=list[CategoryAttributeOutput]),
            APIRoute(path="/", methods=["POST"], handler=ctrl.create_category_attribute, response_model=CategoryAttributeOutput),
            APIRoute(path="/{attribute_id}", methods=["PUT"], handler=ctrl.update_category_attribute, response_model=CategoryAttributeOutput),
            APIRoute(path="/{attribute_id}", methods=["DELETE"], handler=ctrl.delete_category_attribute),
        ])


@dataclass(kw_only=True)
class ProductAttributesRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/products/{product_id}/attributes", tags=["Attributes"])
        ctrl = AttributeController()
        add_api_route(self.router, [
            APIRoute(path="/", methods=["GET"], handler=ctrl.list_product_attribute_values),
            APIRoute(path="/", methods=["POST"], handler=ctrl.set_product_attribute_values),
            APIRoute(path="/{attribute_id}", methods=["DELETE"], handler=ctrl.delete_product_attribute_value),
        ])


