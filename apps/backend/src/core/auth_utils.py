"""
Authentication utilities for controllers
"""

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.security import verify_token

security = HTTPBearer()


async def verify_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify authentication token and return user email"""
    email = verify_token(credentials.credentials)
    if not email:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return email
