from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.config import settings
from core.db import prisma
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
)
from .io import (
    RegisterInput,
    LoginInput,
    TokenResponse,
    TokenOutput,
    UserResponse,
    UserOutput,
    MeUpdateInput,
)


security = HTTPBearer()


@dataclass(kw_only=True)
class AuthController:
    async def register(self, email: str, password: str, name: Optional[str] = None) -> UserResponse:
        existing_user = await prisma.user.find_unique(where={"email": email})
        if existing_user:
            raise HTTPException(status_code=409, detail="email already exists")

        hashed_password = get_password_hash(password)
        new_user = await prisma.user.create(
            data={
                "email": email,
                "name": name,
                "password": hashed_password,
                "status": "inactive",
                "role": "user",
            }
        )
        return UserResponse(data=UserOutput.model_validate(new_user.model_dump()))

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await prisma.user.find_unique(where={"email": email})
        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        if user.status != "active":
            raise HTTPException(status_code=400, detail="Inactive user")

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
        return TokenResponse(data=TokenOutput(access_token=access_token, token_type="bearer"))

    async def me(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
        email = verify_token(credentials.credentials)
        if not email:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        user = await prisma.user.find_unique(where={"email": email})
        if not user:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return UserResponse(data=UserOutput.model_validate(user.model_dump()))

    async def update_me(self, body: MeUpdateInput, credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
        email = verify_token(credentials.credentials)
        if not email:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        current_user = await prisma.user.find_unique(where={"email": email})
        if not current_user:
            raise HTTPException(status_code=401, detail="Could not validate credentials")

        if body.name is not None:
            updated_user = await prisma.user.update(where={"id": current_user.id}, data={"name": body.name})
            return UserResponse(data=UserOutput.model_validate(updated_user.model_dump()))
        return UserResponse(data=UserOutput.model_validate(current_user.model_dump()))

    async def register_with_body(self, body: RegisterInput) -> UserResponse:
        return await self.register(email=body.email, password=body.password, name=body.name)

    async def login_with_body(self, body: LoginInput) -> TokenResponse:
        return await self.login(email=body.email, password=body.password)


