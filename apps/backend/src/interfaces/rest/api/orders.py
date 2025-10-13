from dataclasses import dataclass
from fastapi import APIRouter, Depends
from core.controllers.order import OrderController
from core.controllers.order.io import (
    OrderCreateInput,
    OrderUpdateInput,
    OrderOutput,
    OrderListInput,
    PaymentCreateInput,
    PaymentUpdateInput,
    PaymentOutput
)
from interfaces.rest.utils import APIRoute, add_api_route


@dataclass(kw_only=True)
class OrdersRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/orders", tags=["Orders"])
        order_controller = OrderController()
        add_api_route(self.router, [
            APIRoute(path="/", methods=["POST"], handler=order_controller.create_order, response_model=OrderOutput),
            APIRoute(path="/", methods=["GET"], handler=order_controller.list_orders),
            APIRoute(path="/{order_id}", methods=["GET"], handler=order_controller.get_order, response_model=OrderOutput),
            APIRoute(path="/number/{order_number}", methods=["GET"], handler=order_controller.get_order_by_number, response_model=OrderOutput),
            APIRoute(path="/{order_id}", methods=["PUT"], handler=order_controller.update_order, response_model=OrderOutput),
            APIRoute(path="/{order_id}/cancel", methods=["POST"], handler=order_controller.cancel_order, response_model=OrderOutput),
            APIRoute(path="/{order_id}/payments", methods=["POST"], handler=order_controller.create_payment, response_model=PaymentOutput),
            APIRoute(path="/payments/{payment_id}", methods=["PUT"], handler=order_controller.update_payment, response_model=PaymentOutput),
            # Public guest checkout
            APIRoute(path="/public/create", methods=["POST"], handler=order_controller.public_create_order, response_model=OrderOutput),
        ])
