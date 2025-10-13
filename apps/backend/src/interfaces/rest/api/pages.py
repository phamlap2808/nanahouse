from dataclasses import dataclass
from fastapi import APIRouter
from interfaces.rest.utils import APIRoute, add_api_route
from core.controllers.page import PageController
from core.controllers.page.io import (
    PageCreateInput, PageUpdateInput, PageOutput,
    PageBlockCreateInput, PageBlockUpdateInput, PageBlockReorderInput, PageBlockOutput
)


@dataclass(kw_only=True)
class PagesRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/pages", tags=["Pages"])
        ctrl = PageController()
        add_api_route(self.router, [
            APIRoute(path="/", methods=["GET"], handler=ctrl.list, response_model=list[PageOutput]),
            APIRoute(path="/", methods=["POST"], handler=ctrl.create, response_model=PageOutput),
            APIRoute(path="/{page_id}", methods=["GET"], handler=ctrl.get, response_model=PageOutput),
            APIRoute(path="/{page_id}", methods=["PUT"], handler=ctrl.update, response_model=PageOutput),
            APIRoute(path="/{page_id}", methods=["DELETE"], handler=ctrl.delete),
            # Blocks
            APIRoute(path="/{page_id}/blocks", methods=["GET"], handler=ctrl.list_blocks, response_model=list[PageBlockOutput]),
            APIRoute(path="/{page_id}/blocks", methods=["POST"], handler=ctrl.create_block, response_model=PageBlockOutput),
            APIRoute(path="/{page_id}/blocks/{block_id}", methods=["PUT"], handler=ctrl.update_block, response_model=PageBlockOutput),
            APIRoute(path="/{page_id}/blocks/{block_id}", methods=["DELETE"], handler=ctrl.delete_block),
            APIRoute(path="/{page_id}/blocks/reorder", methods=["POST"], handler=ctrl.reorder_blocks),

            # Sitemap
            APIRoute(path="/sitemap.xml", methods=["GET"], handler=ctrl.sitemap),

            # Public endpoints (read-only)
            APIRoute(path="/public", methods=["GET"], handler=ctrl.public_list, response_model=list[PageOutput]),
            APIRoute(path="/public/slug/{slug}", methods=["GET"], handler=ctrl.public_get_by_slug, response_model=PageOutput),
        ])


