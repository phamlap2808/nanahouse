from dataclasses import dataclass
from typing import List, Optional

from fastapi import APIRouter

from interfaces.rest.utils import APIRoute, add_api_route
from core.controllers.tag import TagController
from core.controllers.tag.io import (
    TagCreateInput,
    TagUpdateInput,
    TagListInput,
    TagOutput,
    TagMergeInput
)


@dataclass(kw_only=True)
class TagsRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/tags", tags=["Tags"])
        tag_controller = TagController()
        add_api_route(self.router, [
            # CRUD operations
            APIRoute(path="/", methods=["GET"], handler=tag_controller.list, response_model=List[TagOutput]),
            APIRoute(path="/", methods=["POST"], handler=tag_controller.create, response_model=TagOutput),
            APIRoute(path="/{tag_id}", methods=["GET"], handler=tag_controller.get, response_model=TagOutput),
            APIRoute(path="/{tag_id}", methods=["PUT"], handler=tag_controller.update, response_model=TagOutput),
            APIRoute(path="/{tag_id}", methods=["DELETE"], handler=tag_controller.delete),
            
            # Tag by slug
            APIRoute(path="/slug/{slug}", methods=["GET"], handler=tag_controller.get_by_slug, response_model=TagOutput),
            
            # Advanced operations
            APIRoute(path="/popular", methods=["GET"], handler=tag_controller.get_popular, response_model=List[TagOutput]),
            APIRoute(path="/{tag_id}/posts", methods=["GET"], handler=tag_controller.get_posts_by_tag),
            APIRoute(path="/{tag_id}/products", methods=["GET"], handler=tag_controller.get_products_by_tag),
            APIRoute(path="/merge", methods=["POST"], handler=tag_controller.merge_tags, response_model=TagOutput),

            # Sitemap
            APIRoute(path="/sitemap.xml", methods=["GET"], handler=tag_controller.sitemap),
        ])
