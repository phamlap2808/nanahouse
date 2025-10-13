from dataclasses import dataclass
from fastapi import APIRouter, Depends
from core.controllers.cart import CartController
from core.controllers.cart.io import (
    CartItemCreateInput,
    CartItemUpdateInput,
    CartOutput,
)
from interfaces.rest.utils import APIRoute, add_api_route


@dataclass(kw_only=True)
class CartRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/cart", tags=["Cart"])
        cart_controller = CartController()
        add_api_route(self.router, [
            APIRoute(path="/", methods=["GET"], handler=cart_controller.get_cart, response_model=CartOutput),
            APIRoute(path="/add", methods=["POST"], handler=cart_controller.add_item, response_model=CartOutput),
            APIRoute(path="/items/{item_id}", methods=["PUT"], handler=cart_controller.update_item, response_model=CartOutput),
            APIRoute(path="/items/{item_id}", methods=["DELETE"], handler=cart_controller.remove_item, response_model=CartOutput),
            APIRoute(path="/clear", methods=["DELETE"], handler=cart_controller.clear_cart, response_model=CartOutput),
            APIRoute(path="/count", methods=["GET"], handler=cart_controller.get_cart_count),
            APIRoute(path="/apply-discount/{code}", methods=["POST"], handler=cart_controller.apply_discount, response_model=CartOutput),
            APIRoute(path="/remove-discount", methods=["POST"], handler=cart_controller.remove_discount, response_model=CartOutput),

            # Public guest cart endpoints
            APIRoute(path="/public", methods=["GET"], handler=cart_controller.public_get_or_create, response_model=CartOutput),
            APIRoute(path="/public/add", methods=["POST"], handler=cart_controller.public_add_item, response_model=CartOutput),
            APIRoute(path="/public/items/{item_id}", methods=["PUT"], handler=cart_controller.public_update_item, response_model=CartOutput),
            APIRoute(path="/public/clear", methods=["POST"], handler=cart_controller.public_clear, response_model=CartOutput),
            APIRoute(path="/public/apply-discount/{code}", methods=["POST"], handler=cart_controller.public_apply_discount, response_model=CartOutput),
            APIRoute(path="/public/remove-discount", methods=["POST"], handler=cart_controller.public_remove_discount, response_model=CartOutput),
        ])
