from dataclasses import dataclass
from fastapi import APIRouter
from interfaces.rest.utils import APIRoute, add_api_route
from core.controllers.media import ProductMediaController
from core.controllers.media.io import (
    ProductMediaCreateInput, ProductMediaUpdateInput, ProductMediaReorderInput, ProductMediaOutput
)


@dataclass(kw_only=True)
class ProductMediaRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/products/{product_id}/media", tags=["Product Media"])
        ctrl = ProductMediaController()
        add_api_route(self.router, [
            APIRoute(path="/", methods=["GET"], handler=ctrl.list, response_model=list[ProductMediaOutput]),
            APIRoute(path="/", methods=["POST"], handler=ctrl.create, response_model=ProductMediaOutput),
            APIRoute(path="/{media_id}", methods=["PUT"], handler=ctrl.update, response_model=ProductMediaOutput),
            APIRoute(path="/{media_id}", methods=["DELETE"], handler=ctrl.delete),
            APIRoute(path="/{media_id}/primary", methods=["POST"], handler=ctrl.set_primary, response_model=ProductMediaOutput),
            APIRoute(path="/reorder", methods=["POST"], handler=ctrl.reorder, response_model=list[ProductMediaOutput]),
        ])


