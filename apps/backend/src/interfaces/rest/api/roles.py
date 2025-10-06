from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter

from interfaces.rest.utils import APIRoute, add_api_route
from core.controllers.role import (
    RoleController,
    RoleCreateInput,
    RoleUpdateInput,
)
from core.controllers.role.io import RoleResponse, RolesResponse


@dataclass(kw_only=True)
class RolesRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/roles", tags=["roles"])
        role_controller = RoleController()
        add_api_route(self.router, [
            APIRoute(path="/", methods=["GET"], handler=role_controller.list, response_model=RolesResponse),
            APIRoute(path="/", methods=["POST"], handler=role_controller.create_with_body, response_model=RoleResponse),
            APIRoute(path="/{role_id}", methods=["GET"], handler=role_controller.get, response_model=RoleResponse),
            APIRoute(path="/{role_id}", methods=["PUT"], handler=role_controller.update_with_body, response_model=RoleResponse),
            APIRoute(path="/{role_id}", methods=["DELETE"], handler=role_controller.delete, response_model=RoleResponse),
            APIRoute(path="/{role_id}/permissions/{permission_id}", methods=["POST"], handler=role_controller.assign_permission),
            APIRoute(path="/{role_id}/permissions/{permission_id}", methods=["DELETE"], handler=role_controller.remove_permission),
        ])
