from dataclasses import dataclass
from typing import List, Optional

from fastapi import APIRouter

from interfaces.rest.utils import APIRoute, add_api_route
from core.controllers.category import CategoryController
from core.controllers.category.io import (
    CategoryCreateInput,
    CategoryUpdateInput,
    CategoryListInput,
    CategoryOutput,
    CategoryTreeOutput
)


@dataclass(kw_only=True)
class CategoriesRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/categories", tags=["Categories"])
        category_controller = CategoryController()
        add_api_route(self.router, [
            # CRUD operations
            APIRoute(path="/", methods=["GET"], handler=category_controller.list, response_model=List[CategoryOutput]),
            APIRoute(path="/", methods=["POST"], handler=category_controller.create, response_model=CategoryOutput),
            APIRoute(path="/{category_id}", methods=["GET"], handler=category_controller.get, response_model=CategoryOutput),
            APIRoute(path="/{category_id}", methods=["PUT"], handler=category_controller.update, response_model=CategoryOutput),
            APIRoute(path="/{category_id}", methods=["DELETE"], handler=category_controller.delete),
            
            # Tree operations
            APIRoute(path="/tree", methods=["GET"], handler=category_controller.get_tree, response_model=List[CategoryTreeOutput]),
            APIRoute(path="/slug/{slug}", methods=["GET"], handler=category_controller.get_by_slug, response_model=CategoryOutput),
            
            # Advanced operations
            APIRoute(path="/{category_id}/move", methods=["PATCH"], handler=category_controller.move_to_parent, response_model=CategoryOutput),
            APIRoute(path="/reorder", methods=["PATCH"], handler=category_controller.reorder),

            # Sitemap
            APIRoute(path="/sitemap.xml", methods=["GET"], handler=category_controller.sitemap),

            # Public endpoints (read-only)
            APIRoute(path="/public", methods=["GET"], handler=category_controller.public_list, response_model=List[CategoryOutput]),
            APIRoute(path="/public/slug/{slug}", methods=["GET"], handler=category_controller.public_get_by_slug, response_model=CategoryOutput),
        ])