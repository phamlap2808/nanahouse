from dataclasses import dataclass
from typing import Optional, List

from fastapi import HTTPException

from core.db import prisma
from .io import UserOutput, UserResponse, UsersResponse


@dataclass(kw_only=True)
class UserController:
    async def create(self, email: str, password: str, name: Optional[str] = None) -> UserResponse:
        existing = await prisma.user.find_unique(where={"email": email})
        if existing:
            raise HTTPException(status_code=409, detail="email already exists")
        user = await prisma.user.create(data={"email": email, "password": password, "name": name})
        return UserResponse(data=UserOutput.model_validate(user.model_dump()))

    async def get(self, user_id: int) -> UserResponse:
        user = await prisma.user.find_unique(where={"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="user not found")
        return UserResponse(data=UserOutput.model_validate(user.model_dump()))

    async def list(self) -> UsersResponse:
        users = await prisma.user.find_many()
        return UsersResponse(data=[UserOutput.model_validate(u.model_dump()) for u in users])

    async def delete(self, user_id: int) -> UserResponse:
        user = await prisma.user.delete(where={"id": user_id})
        return UserResponse(data=UserOutput.model_validate(user.model_dump()))


