from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter

from interfaces.rest.utils import APIRoute, add_api_route
from core.controllers.permission import (
    PermissionController,
    PermissionCreateInput,
    PermissionUpdateInput,
)
from core.controllers.permission.io import PermissionResponse, PermissionsResponse


@dataclass(kw_only=True)
class PermissionsRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/permissions", tags=["permissions"])
        permission_controller = PermissionController()
        add_api_route(self.router, [
            APIRoute(path="/", methods=["GET"], handler=permission_controller.list, response_model=PermissionsResponse),
            APIRoute(path="/", methods=["POST"], handler=permission_controller.create_with_body, response_model=PermissionResponse),
            APIRoute(path="/{permission_id}", methods=["GET"], handler=permission_controller.get, response_model=PermissionResponse),
            APIRoute(path="/{permission_id}", methods=["PUT"], handler=permission_controller.update_with_body, response_model=PermissionResponse),
            APIRoute(path="/{permission_id}", methods=["DELETE"], handler=permission_controller.delete, response_model=PermissionResponse),
            APIRoute(path="/resource/{resource}", methods=["GET"], handler=permission_controller.list_by_resource, response_model=PermissionsResponse),
        ])
