from dataclasses import dataclass
from fastapi import APIRouter
from interfaces.rest.utils import APIRoute, add_api_route
from core.controllers.collection import CollectionController
from core.controllers.collection.io import (
    CollectionCreateInput, CollectionUpdateInput, CollectionOutput,
    CollectionProductAddInput, CollectionProductReorderInput
)


@dataclass(kw_only=True)
class CollectionsRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/collections", tags=["Collections"])
        ctrl = CollectionController()
        add_api_route(self.router, [
            APIRoute(path="/", methods=["GET"], handler=ctrl.list, response_model=list[CollectionOutput]),
            APIRoute(path="/", methods=["POST"], handler=ctrl.create, response_model=CollectionOutput),
            APIRoute(path="/{collection_id}", methods=["GET"], handler=ctrl.get, response_model=CollectionOutput),
            APIRoute(path="/{collection_id}", methods=["PUT"], handler=ctrl.update, response_model=CollectionOutput),
            APIRoute(path="/{collection_id}", methods=["DELETE"], handler=ctrl.delete),
            APIRoute(path="/{collection_id}/products", methods=["POST"], handler=ctrl.add_product),
            APIRoute(path="/{collection_id}/products/{product_id}", methods=["DELETE"], handler=ctrl.remove_product),
            APIRoute(path="/{collection_id}/products/reorder", methods=["POST"], handler=ctrl.reorder_products),
        ])


