from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from app.application.dto.auth import SignupRequest, LoginRequest, AuthResponse, UserResponse
from app.infrastructure.database import AsyncSessionLocal, User
from app.infrastructure.security.auth import hash_password, verify_password, create_access_token
from app.domain.enums.user import Role

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def user_response(user: User) -> UserResponse:
    return UserResponse(id=user.id, email=user.email, name=user.name, role=user.role.value)


@router.post("/signup", response_model=AuthResponse, status_code=201)
async def signup(payload: SignupRequest):
    email = payload.email.lower()
    async with AsyncSessionLocal() as session:
        existing = await session.scalar(select(User).where(User.email == email))
        if existing:
            raise HTTPException(status_code=409, detail="An account with this email already exists.")
        user = User(email=email, name=payload.name, password_hash=hash_password(payload.password), role=Role.CUSTOMER)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return AuthResponse(access_token=create_access_token(user.id, user.email, user.role), user=user_response(user))


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    email = payload.email.lower()
    async with AsyncSessionLocal() as session:
        user = await session.scalar(select(User).where(User.email == email))
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.", headers={"WWW-Authenticate": "Bearer"})
        return AuthResponse(access_token=create_access_token(user.id, user.email, user.role), user=user_response(user))
