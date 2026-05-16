"""Authentication API endpoints."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_auth_service, get_current_user
from app.api.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse, RefreshTokenRequest
from app.application.auth_service import AuthService
from app.domain.entities.user import UserEntity
from app.domain.exceptions import AuthenticationException, DuplicateEntityException
from app.infrastructure.security.jwt_handler import decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, auth_service: Annotated[AuthService, Depends(get_auth_service)]):
    """Register a new user account. Allows choosing between ATTENDEE and ORGANIZER."""
    try:
        from app.domain.enums import UserRole
        
        # Security: Prevent self-registration as ADMIN
        requested_role = UserRole.ATTENDEE
        if request.role:
            try:
                requested_role = UserRole(request.role.lower())
                if requested_role == UserRole.ADMIN:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN, 
                        detail="Cannot register as administrator"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Invalid role: {request.role}"
                )

        user = auth_service.register(
            email=request.email, 
            password=request.password, 
            full_name=request.full_name,
            role=requested_role
        )
        return UserResponse(
            id=user.id, 
            email=user.email, 
            full_name=user.full_name, 
            role=user.role.value, 
            is_active=user.is_active
        )
    except DuplicateEntityException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, auth_service: Annotated[AuthService, Depends(get_auth_service)]):
    """Authenticate a user and return access and refresh tokens."""
    try:
        user, access, refresh = auth_service.login(email=request.email, password=request.password)
        return TokenResponse(access_token=access, refresh_token=refresh)
    except AuthenticationException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, auth_service: Annotated[AuthService, Depends(get_auth_service)]):
    """Generate new tokens using a valid refresh token."""
    payload = decode_access_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    
    try:
        user_id = int(payload.get("sub"))
        access, refresh = auth_service.refresh_tokens(user_id)
        return TokenResponse(access_token=access, refresh_token=refresh)
    except (AuthenticationException, ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not refresh tokens")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[UserEntity, Depends(get_current_user)]):
    """Retrieve the currently authenticated user's profile."""
    return UserResponse(
        id=current_user.id, 
        email=current_user.email, 
        full_name=current_user.full_name, 
        role=current_user.role.value, 
        is_active=current_user.is_active
    )
