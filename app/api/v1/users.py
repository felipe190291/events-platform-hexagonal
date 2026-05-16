"""User management API endpoints for administrators."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_current_user, get_user_repo
from app.api.schemas.auth import UserResponse, PaginatedUserResponse
from app.domain.entities.user import UserEntity
from app.domain.enums import UserRole
from app.domain.ports.user_repository import UserRepositoryPort
from pydantic import BaseModel
import math

router = APIRouter(prefix="/users", tags=["User Management"])

class RoleUpdateRequest(BaseModel):
    role: UserRole

def ensure_admin(current_user: UserEntity):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador para esta acción"
        )

@router.get("", response_model=PaginatedUserResponse)
def list_users(
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    user_repo: Annotated[UserRepositoryPort, Depends(get_user_repo)],
    query: str | None = None,
    role: UserRole | None = None,
    page: int = 1,
    size: int = 10
):
    """List and search users with pagination and role filter (Admin only)."""
    ensure_admin(current_user)
    
    skip = (page - 1) * size
    users, total = user_repo.search(query=query, role=role, skip=skip, limit=size)
    
    user_list = [
        UserResponse(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=u.role.value,
            is_active=u.is_active
        ) for u in users
    ]
    
    return PaginatedUserResponse(
        users=user_list,
        total=total,
        page=page,
        size=size,
        pages=math.ceil(total / size) if total > 0 else 1
    )

@router.patch("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    request: RoleUpdateRequest,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    user_repo: Annotated[UserRepositoryPort, Depends(get_user_repo)]
):
    """Update a user's role (Admin only)."""
    ensure_admin(current_user)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.role = request.role
    updated_user = user_repo.update(user)
    
    return UserResponse(
        id=updated_user.id,
        email=updated_user.email,
        full_name=updated_user.full_name,
        role=updated_user.role.value,
        is_active=updated_user.is_active
    )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: Annotated[UserEntity, Depends(get_current_user)],
    user_repo: Annotated[UserRepositoryPort, Depends(get_user_repo)]
):
    """Delete a user (Admin only)."""
    ensure_admin(current_user)
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propia cuenta de administrador"
        )
        
    success = user_repo.delete(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return None
