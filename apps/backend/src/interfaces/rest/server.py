from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.db import connect_db, disconnect_db
from .api.test import TestRouter
from .api.users import UsersRouter
from .api.auth import AuthRouter
from .api.groups import GroupsRouter
from .api.roles import RolesRouter
from .api.permissions import PermissionsRouter
from .api.categories import CategoriesRouter
from .api.products import ProductsRouter
from .api.blog import BlogRouter
from .api.tags import TagsRouter
from .api.expenses import ExpenseCategoriesRouter, ExpensesRouter
from .api.cart import CartRouter
from .api.orders import OrdersRouter
from .api.product_variants import ProductOptionsRouter, ProductVariantsRouter
from .api.product_media import ProductMediaRouter
from .api.collections import CollectionsRouter
from .api.attributes import CategoryAttributesRouter, ProductAttributesRouter
from .api.discounts import DiscountsRouter
from .api.pages import PagesRouter
from .middleware.gauth import JwtAuthMiddleware
from .middleware.rbac import RBACMiddleware
from .middleware.rate_limit import SimpleRateLimitMiddleware
from core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    try:
        yield
    finally:
        await disconnect_db()


test_router = TestRouter()
users_router = UsersRouter()
groups_router = GroupsRouter()
roles_router = RolesRouter()
permissions_router = PermissionsRouter()
categories_router = CategoriesRouter()
products_router = ProductsRouter()
blog_router = BlogRouter()
tags_router = TagsRouter()
# Instantiate class-based routers
cart_router = CartRouter()
orders_router = OrdersRouter()
product_options_router = ProductOptionsRouter()
product_variants_router = ProductVariantsRouter()
product_media_router = ProductMediaRouter()
collections_router = CollectionsRouter()
category_attributes_router = CategoryAttributesRouter()
product_attributes_router = ProductAttributesRouter()
discounts_router = DiscountsRouter()
pages_router = PagesRouter()
expense_categories_router = ExpenseCategoriesRouter()
expenses_router = ExpensesRouter()

app = FastAPI(title=settings.app_name, root_path="/api", lifespan=lifespan)

auth_router = AuthRouter()
app.include_router(auth_router.router)
app.include_router(test_router.router)
app.include_router(users_router.router)
app.include_router(groups_router.router)
app.include_router(roles_router.router)
app.include_router(permissions_router.router)
app.include_router(categories_router.router)
app.include_router(products_router.router)
app.include_router(blog_router.router)
app.include_router(tags_router.router)
app.include_router(cart_router.router)
app.include_router(orders_router.router)
app.include_router(product_options_router.router)
app.include_router(product_variants_router.router)
app.include_router(product_media_router.router)
app.include_router(collections_router.router)
app.include_router(category_attributes_router.router)
app.include_router(product_attributes_router.router)
app.include_router(discounts_router.router)
app.include_router(pages_router.router)
app.include_router(expense_categories_router.router)
app.include_router(expenses_router.router)

# Add JWT auth middleware for API routes, excluding auth endpoints
app.add_middleware(
    JwtAuthMiddleware,
    exclude_paths=[
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/forgot-password",
        "/api/auth/reset-password",
        "/api/auth/verify-email",
        "/api/test/health",
        "/api/blog/public",
        "/api/blog/rss",
        "/api/blog/sitemap.xml",
        "/api/blog/sitemap_index.xml",
        "/api/tags/sitemap.xml",
        "/api/categories/sitemap.xml",
        "/api/pages/sitemap.xml",
        "/api/products/public",
        "/api/categories/public",
        "/api/pages/public",
        "/api/cart/public",
        "/api/orders/public",
        "/api/docs",
        "/api/openapi.json"
    ],
)

# Add RBAC middleware for permission checking
app.add_middleware(
    RBACMiddleware,
    exclude_paths=[
        "/api/auth/login",
        "/api/auth/register",
        "/api/test/health",
        "/api/auth/me",  # User có thể xem thông tin của chính mình
        "/api/docs",
        "/api/openapi.json"
    ],
)

# Add simple rate limit for public endpoints
app.add_middleware(
    SimpleRateLimitMiddleware,
    include_paths=[
        "/api/auth/forgot-password",
        "/api/auth/reset-password",
        "/api/auth/verify-email",
        "/api/cart/public",
        "/api/orders/public",
        "/api/blog/public",
        "/api/products/public",
        "/api/pages/public",
    ],
)