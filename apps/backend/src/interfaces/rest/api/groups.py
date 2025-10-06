from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter

from interfaces.rest.utils import APIRoute, add_api_route
from core.controllers.group import (
    GroupController,
    GroupCreateInput,
    GroupUpdateInput,
)
from core.controllers.group.io import GroupResponse, GroupsResponse


@dataclass(kw_only=True)
class GroupsRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/groups", tags=["groups"])
        group_controller = GroupController()
        add_api_route(self.router, [
            APIRoute(path="/", methods=["GET"], handler=group_controller.list, response_model=GroupsResponse),
            APIRoute(path="/", methods=["POST"], handler=group_controller.create_with_body, response_model=GroupResponse),
            APIRoute(path="/{group_id}", methods=["GET"], handler=group_controller.get, response_model=GroupResponse),
            APIRoute(path="/{group_id}", methods=["PUT"], handler=group_controller.update_with_body, response_model=GroupResponse),
            APIRoute(path="/{group_id}", methods=["DELETE"], handler=group_controller.delete, response_model=GroupResponse),
            APIRoute(path="/{group_id}/users/{user_id}", methods=["POST"], handler=group_controller.add_user),
            APIRoute(path="/{group_id}/users/{user_id}", methods=["DELETE"], handler=group_controller.remove_user),
            APIRoute(path="/{group_id}/roles/{role_id}", methods=["POST"], handler=group_controller.assign_role),
            APIRoute(path="/{group_id}/roles/{role_id}", methods=["DELETE"], handler=group_controller.remove_role),
        ])
