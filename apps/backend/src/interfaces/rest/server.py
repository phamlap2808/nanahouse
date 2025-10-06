from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.db import connect_db, disconnect_db
from .api.test import TestRouter
from .api.users import UsersRouter
from .api.auth import AuthRouter
from .api.groups import GroupsRouter
from .api.roles import RolesRouter
from .api.permissions import PermissionsRouter
from .middleware.gauth import JwtAuthMiddleware
from .middleware.rbac import RBACMiddleware
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

app = FastAPI(title=settings.app_name, root_path="/api", lifespan=lifespan)

auth_router = AuthRouter()
app.include_router(auth_router.router)
app.include_router(test_router.router)
app.include_router(users_router.router)
app.include_router(groups_router.router)
app.include_router(roles_router.router)
app.include_router(permissions_router.router)

# Add JWT auth middleware for API routes, excluding auth endpoints
app.add_middleware(
    JwtAuthMiddleware,
    exclude_paths=[
        "/api/auth/login",
        "/api/auth/register",
        "/api/test/health",
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