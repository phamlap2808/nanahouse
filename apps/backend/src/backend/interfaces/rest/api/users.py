from dataclasses import dataclass
from typing import Optional

from fastapi import APIRouter

from backend.interfaces.rest.utils import APIRoute, add_api_route
from backend.core.controllers.user import (
    UserController,
    UserCreateInput,
)
from backend.core.controllers.user.io import UserResponse, UsersResponse


@dataclass(kw_only=True)
class UsersRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/users", tags=["users"])
        user_controller = UserController()
        add_api_route(self.router, [
            APIRoute(path="/", methods=["GET"], handler=user_controller.list, response_model=UsersResponse),
            APIRoute(path="/", methods=["POST"], handler=user_controller.create, response_model=UserResponse),
            APIRoute(path="/{user_id}", methods=["GET"], handler=user_controller.get, response_model=UserResponse),
            APIRoute(path="/{user_id}", methods=["DELETE"], handler=user_controller.delete, response_model=UserResponse),
        ])


