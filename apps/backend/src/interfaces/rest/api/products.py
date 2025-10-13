from dataclasses import dataclass
from typing import List, Optional

from fastapi import APIRouter

from interfaces.rest.utils import APIRoute, add_api_route
from core.controllers.product import ProductController
from core.controllers.product.io import (
    ProductCreateInput,
    ProductUpdateInput,
    ProductListInput,
    ProductOutput
)


@dataclass(kw_only=True)
class ProductsRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/products", tags=["Products"])
        product_controller = ProductController()
        add_api_route(self.router, [
            # CRUD operations
            APIRoute(path="/", methods=["GET"], handler=product_controller.list, response_model=List[ProductOutput]),
            APIRoute(path="/", methods=["POST"], handler=product_controller.create, response_model=ProductOutput),
            APIRoute(path="/{product_id}", methods=["GET"], handler=product_controller.get, response_model=ProductOutput),
            APIRoute(path="/{product_id}", methods=["PUT"], handler=product_controller.update, response_model=ProductOutput),
            APIRoute(path="/{product_id}", methods=["DELETE"], handler=product_controller.delete),
            
            # Product by slug
            APIRoute(path="/slug/{slug}", methods=["GET"], handler=product_controller.get_by_slug, response_model=ProductOutput),
            
            # Advanced operations
            APIRoute(path="/{product_id}/stock", methods=["PATCH"], handler=product_controller.update_stock, response_model=ProductOutput),
            APIRoute(path="/{product_id}/featured", methods=["PATCH"], handler=product_controller.toggle_featured, response_model=ProductOutput),
            APIRoute(path="/{product_id}/status", methods=["PATCH"], handler=product_controller.update_status, response_model=ProductOutput),

            # Public endpoints (read-only)
            APIRoute(path="/public", methods=["GET"], handler=product_controller.public_list, response_model=List[ProductOutput]),
            APIRoute(path="/public/slug/{slug}", methods=["GET"], handler=product_controller.public_get_by_slug, response_model=ProductOutput),
        ])
