from dataclasses import dataclass
from fastapi import APIRouter
from interfaces.rest.utils import APIRoute, add_api_route
from core.controllers.discount import DiscountController
from core.controllers.discount.io import (
    DiscountCreateInput, DiscountUpdateInput, DiscountOutput
)


@dataclass(kw_only=True)
class DiscountsRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/discounts", tags=["Discounts"])
        ctrl = DiscountController()
        add_api_route(self.router, [
            APIRoute(path="/", methods=["GET"], handler=ctrl.list, response_model=list[DiscountOutput]),
            APIRoute(path="/", methods=["POST"], handler=ctrl.create, response_model=DiscountOutput),
            APIRoute(path="/{discount_id}", methods=["GET"], handler=ctrl.get, response_model=DiscountOutput),
            APIRoute(path="/{discount_id}", methods=["PUT"], handler=ctrl.update, response_model=DiscountOutput),
            APIRoute(path="/{discount_id}", methods=["DELETE"], handler=ctrl.delete),
            APIRoute(path="/{discount_id}/activate", methods=["POST"], handler=ctrl.activate),
            APIRoute(path="/{discount_id}/deactivate", methods=["POST"], handler=ctrl.deactivate),
        ])


