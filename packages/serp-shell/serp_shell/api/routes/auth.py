"""
Authentication routes
"""

from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()


class LoginRequest(BaseModel):
    # Accept either username or email
    username: str | None = None
    email: str | None = None
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    permissions: List[str] = []


class LoginResponse(BaseModel):
    accessToken: str
    user: UserResponse


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Authenticate user and return JWT token.

    This is a placeholder - actual implementation should be in serp-users module.
    """
    # TODO: Implement actual authentication
    # Accept either username or email field
    login_id = credentials.email or credentials.username
    if login_id == "admin@example.com" and credentials.password == "admin":
        return LoginResponse(
            accessToken="sample_token_replace_with_jwt",
            user=UserResponse(
                id="1",
                email="admin@example.com",
                name="Admin User",
                permissions=["*"],  # Admin has all permissions
            ),
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/logout")
async def logout():
    """Logout current user"""
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user():
    """Get current authenticated user"""
    # TODO: Implement user retrieval from token
    return UserResponse(
        id="1",
        email="admin@example.com",
        name="Admin User",
        permissions=["*"],
    )
