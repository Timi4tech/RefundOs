from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy import select
from app.core.config import settings
from app.infrastructure.database import AsyncSessionLocal, User
from app.domain.enums.user import Role

password_hash = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)

@dataclass(frozen=True)
class AuthenticatedUser:
    id: str
    email: str
    role: Role

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    try:
        return password_hash.verify(password, hashed)
    except Exception:
        return False

def create_access_token(user_id: str, email: str, role: Role) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": user_id, "email": email, "role": role.value, "iat": now, "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> AuthenticatedUser:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = str(payload["sub"])
        email = str(payload["email"])
        role = Role(payload["role"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token.", headers={"WWW-Authenticate": "Bearer"})
    async with AsyncSessionLocal() as session:
        user = await session.scalar(select(User).where(User.id == user_id))
        if user is None or user.email != email or user.role != role:
            raise HTTPException(status_code=401, detail="Authentication session is no longer valid.", headers={"WWW-Authenticate": "Bearer"})
    return AuthenticatedUser(id=user_id, email=email, role=role)
