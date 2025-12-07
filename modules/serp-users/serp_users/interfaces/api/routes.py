"""API routes for users module."""

from fastapi import APIRouter, Depends, Header, HTTPException, status

from serp_users.application.dto import (
    LoginDTO,
    PasswordChangeDTO,
    TokenDTO,
    UserCreateDTO,
    UserDTO,
    UserUpdateDTO,
)
from serp_users.application.services import AuthService, UserService
from serp_users.config import UsersSettings
from serp_users.domain.services import PasswordHasher
from serp_users.infrastructure.repositories import (
    InMemorySessionRepository,
    InMemoryUserRepository,
)

# Create router
router = APIRouter(prefix="/api/users", tags=["users"])

# Dependencies
_user_repo = InMemoryUserRepository()
_session_repo = InMemorySessionRepository()
_password_hasher = PasswordHasher()
_settings = UsersSettings()


def get_user_service() -> UserService:
    """Get user service dependency."""
    return UserService(_user_repo, _password_hasher)


def get_auth_service() -> AuthService:
    """Get auth service dependency."""
    return AuthService(_user_repo, _session_repo, _password_hasher, _settings)


async def get_current_user(
    authorization: str = Header(...),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserDTO:
    """Get current authenticated user."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    token = authorization.replace("Bearer ", "")
    try:
        return await auth_service.verify_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


# Authentication routes
@router.post("/auth/login", response_model=TokenDTO, status_code=status.HTTP_200_OK)
async def login(
    data: LoginDTO,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenDTO:
    """Login user and get access token."""
    try:
        return await auth_service.login(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    authorization: str = Header(...),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    """Logout user and revoke session."""
    token = authorization.replace("Bearer ", "")
    await auth_service.logout(token)


@router.post("/auth/refresh", response_model=TokenDTO, status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenDTO:
    """Refresh access token."""
    try:
        return await auth_service.refresh_token(refresh_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.get("/auth/me", response_model=UserDTO, status_code=status.HTTP_200_OK)
async def get_me(
    current_user: UserDTO = Depends(get_current_user),
) -> UserDTO:
    """Get current authenticated user."""
    return current_user


# User management routes
@router.get("", response_model=list[UserDTO], status_code=status.HTTP_200_OK)
async def list_users(
    user_service: UserService = Depends(get_user_service),
    current_user: UserDTO = Depends(get_current_user),
) -> list[UserDTO]:
    """List all users."""
    users = await user_service._users.find_all()
    return [user_service._to_dto(u) for u in users]


@router.get("/{user_id}", response_model=UserDTO, status_code=status.HTTP_200_OK)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: UserDTO = Depends(get_current_user),
) -> UserDTO:
    """Get user by ID."""
    try:
        return await user_service.get_user(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreateDTO,
    user_service: UserService = Depends(get_user_service),
    current_user: UserDTO = Depends(get_current_user),
) -> UserDTO:
    """Create a new user."""
    try:
        return await user_service.create_user(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{user_id}", response_model=UserDTO, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: str,
    data: UserUpdateDTO,
    user_service: UserService = Depends(get_user_service),
    current_user: UserDTO = Depends(get_current_user),
) -> UserDTO:
    """Update user."""
    try:
        return await user_service.update_user(user_id, data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: UserDTO = Depends(get_current_user),
) -> None:
    """Delete user."""
    try:
        await user_service.delete_user(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{user_id}/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user_id: str,
    data: PasswordChangeDTO,
    user_service: UserService = Depends(get_user_service),
    current_user: UserDTO = Depends(get_current_user),
) -> None:
    """Change user password."""
    # Users can only change their own password unless they're superuser
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change other user's password",
        )

    try:
        await user_service.change_password(user_id, data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{user_id}/permissions", response_model=list[str], status_code=status.HTTP_200_OK
)
async def get_user_permissions(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: UserDTO = Depends(get_current_user),
) -> list[str]:
    """Get user permissions."""
    try:
        user = await user_service.get_user(user_id)
        return user.permissions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
