from dataclasses import dataclass

from fastapi import APIRouter

from backend.interfaces.rest.utils import APIRoute, add_api_route
from backend.core.controllers.auth.controller import AuthController
from backend.core.controllers.auth.io import (
    RegisterInput,
    LoginInput,
    MeUpdateInput,
    UserResponse,
    TokenResponse,
)


@dataclass(kw_only=True)
class AuthRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/auth", tags=["authentication"])
        controller = AuthController()
        add_api_route(
            self.router,
            [
                APIRoute(path="/register", methods=["POST"], handler=controller.register_with_body, response_model=UserResponse),
                APIRoute(path="/login", methods=["POST"], handler=controller.login_with_body, response_model=TokenResponse),
                APIRoute(path="/me", methods=["GET"], handler=controller.me, response_model=UserResponse),
                APIRoute(path="/me", methods=["PUT"], handler=controller.update_me, response_model=UserResponse),
            ],
        )


