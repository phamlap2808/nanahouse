from dataclasses import dataclass
from typing import List, Optional

from fastapi import APIRouter

from interfaces.rest.utils import APIRoute, add_api_route
from core.controllers.blog import BlogController
from core.controllers.blog.io import (
    PostCreateInput,
    PostUpdateInput,
    PostListInput,
    PostOutput,
    TagCreateInput,
    TagUpdateInput,
    TagOutput,
    CommentCreateInput,
    CommentUpdateInput,
    CommentOutput,
)


@dataclass(kw_only=True)
class BlogRouter:
    def __post_init__(self):
        self.router = APIRouter(prefix="/blog", tags=["Blog"])
        blog_controller = BlogController()
        add_api_route(self.router, [
            # Post CRUD operations
            APIRoute(path="/posts", methods=["GET"], handler=blog_controller.list_posts, response_model=List[PostOutput]),
            APIRoute(path="/posts", methods=["POST"], handler=blog_controller.create_post, response_model=PostOutput),
            APIRoute(path="/posts/{post_id}", methods=["GET"], handler=blog_controller.get_post, response_model=PostOutput),
            APIRoute(path="/posts/{post_id}", methods=["PUT"], handler=blog_controller.update_post, response_model=PostOutput),
            APIRoute(path="/posts/{post_id}", methods=["DELETE"], handler=blog_controller.delete_post),
            
            # Post by slug
            APIRoute(path="/posts/slug/{slug}", methods=["GET"], handler=blog_controller.get_post_by_slug, response_model=PostOutput),
            
            # Post advanced operations
            APIRoute(path="/posts/{post_id}/publish", methods=["PATCH"], handler=blog_controller.publish_post, response_model=PostOutput),
            APIRoute(path="/posts/{post_id}/view", methods=["PATCH"], handler=blog_controller.increment_view),
            
            # Tag CRUD operations
            APIRoute(path="/tags", methods=["GET"], handler=blog_controller.list_tags, response_model=List[TagOutput]),
            APIRoute(path="/tags", methods=["POST"], handler=blog_controller.create_tag, response_model=TagOutput),
            APIRoute(path="/tags/{tag_id}", methods=["GET"], handler=blog_controller.get_tag, response_model=TagOutput),
            APIRoute(path="/tags/{tag_id}", methods=["PUT"], handler=blog_controller.update_tag, response_model=TagOutput),
            APIRoute(path="/tags/{tag_id}", methods=["DELETE"], handler=blog_controller.delete_tag),

            # Comments under posts
            APIRoute(path="/posts/{post_id}/comments", methods=["GET"], handler=blog_controller.list_post_comments, response_model=List[CommentOutput]),
            APIRoute(path="/posts/{post_id}/comments", methods=["POST"], handler=blog_controller.create_post_comment, response_model=CommentOutput),
            APIRoute(path="/posts/{post_id}/comments/{comment_id}", methods=["PUT"], handler=blog_controller.update_post_comment, response_model=CommentOutput),
            APIRoute(path="/posts/{post_id}/comments/{comment_id}", methods=["DELETE"], handler=blog_controller.delete_post_comment),

            # Public endpoints
            APIRoute(path="/public/posts", methods=["GET"], handler=blog_controller.public_list_posts, response_model=List[PostOutput]),
            APIRoute(path="/public/posts/slug/{slug}", methods=["GET"], handler=blog_controller.public_get_post_by_slug),

            # RSS feed
            APIRoute(path="/rss", methods=["GET"], handler=blog_controller.rss_feed),

            # Sitemap
            APIRoute(path="/sitemap.xml", methods=["GET"], handler=blog_controller.sitemap),

            # Sitemap index (aggregate)
            APIRoute(path="/sitemap_index.xml", methods=["GET"], handler=blog_controller.sitemap_index),

            # Structured data JSON-LD for a post
            APIRoute(path="/public/posts/slug/{slug}/structured-data", methods=["GET"], handler=blog_controller.public_post_structured_data),
        ])
