from dataclasses import dataclass

from fastapi import APIRouter
from backend.interfaces.rest.utils import APIRoute, add_api_route

@dataclass(kw_only=True)
class TestRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/test", tags=["test"])
        add_api_route(self.router, [
            APIRoute(path="/health", methods=["GET"], handler=self.health),
        ])

    def health(self):
        return {"status": "ok"}
