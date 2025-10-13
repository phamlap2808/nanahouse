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
    ForgotPasswordInput,
    ResetPasswordInput,
    VerifyEmailInput,
)
from core.services.notify import send_email
import secrets
from datetime import datetime, timezone, timedelta


security = HTTPBearer()


@dataclass(kw_only=True)
class AuthController:
    async def register(self, email: str, password: str, name: Optional[str] = None) -> UserResponse:
        existing_user = await prisma.user.find_unique(where={"email": email})
        if existing_user:
            raise HTTPException(status_code=409, detail="email already exists")

        try:
            hashed_password = get_password_hash(password)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=422, detail="Invalid password format")

        new_user = await prisma.user.create(
            data={
                "email": email,
                "name": name,
                "password": hashed_password,
                "status": "inactive",
            }
        )
        # Create verification token and send email
        import secrets
        from datetime import datetime, timezone, timedelta
        token = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(hours=24)
        await prisma.emailverificationtoken.create(data={
            "userId": new_user.id,
            "token": token,
            "expiresAt": expires
        })

        from core.config import settings
        from core.services.notify import send_email
        verify_url = f"{settings.site_base_url}/verify-email?token={token}"
        send_email(
            to_email=new_user.email,
            subject="Xác thực tài khoản",
            html_body=f"<p>Chào {new_user.name or new_user.email},</p><p>Vui lòng xác thực tài khoản bằng cách nhấp: <a href=\"{verify_url}\">Xác thực</a></p>"
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

    async def forgot_password(self, body: ForgotPasswordInput) -> dict:
        user = await prisma.user.find_unique(where={"email": body.email})
        if not user:
            # Không lộ thông tin user tồn tại hay không
            return {"message": "If the email exists, a reset link has been sent"}

        token = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(hours=2)
        await prisma.passwordresettoken.create(data={
            "userId": user.id,
            "token": token,
            "expiresAt": expires
        })

        reset_url = f"{settings.site_base_url}/reset-password?token={token}"
        send_email(
            to_email=body.email,
            subject="Reset your password",
            html_body=f"<p>Click the link to reset your password:</p><p><a href=\"{reset_url}\">Reset Password</a></p>"
        )
        return {"message": "If the email exists, a reset link has been sent"}

    async def reset_password(self, body: ResetPasswordInput) -> dict:
        prt = await prisma.passwordresettoken.find_unique(where={"token": body.token}, include={"user": True})
        if not prt or prt.usedAt is not None or (prt.expiresAt and prt.expiresAt < datetime.now(timezone.utc)):
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        hashed = get_password_hash(body.new_password)
        await prisma.user.update(where={"id": prt.userId}, data={"password": hashed})
        await prisma.passwordresettoken.update(where={"id": prt.id}, data={"usedAt": datetime.now(timezone.utc)})
        return {"message": "Password has been reset"}

    async def verify_email(self, body: VerifyEmailInput) -> dict:
        from datetime import datetime, timezone
        tok = await prisma.emailverificationtoken.find_unique(where={"token": body.token}, include={"user": True})
        if not tok or tok.usedAt is not None or (tok.expiresAt and tok.expiresAt < datetime.now(timezone.utc)):
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        await prisma.user.update(where={"id": tok.userId}, data={"status": "active"})
        await prisma.emailverificationtoken.update(where={"id": tok.id}, data={"usedAt": datetime.now(timezone.utc)})
        return {"message": "Email verified"}

