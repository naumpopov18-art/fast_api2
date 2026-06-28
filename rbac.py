from fastapi import HTTPException, status
from app.models import User

ROLE_PERMISSIONS = {
    "admin": [
        "user:create", "user:read", "user:update", "user:delete",
        "user:list", "user:change_role",
        "advertisement:create", "advertisement:read", 
        "advertisement:update", "advertisement:delete"
    ],
    "user": [
        "user:read", "user:update_self", "user:delete_self",
        "advertisement:create", "advertisement:read",
        "advertisement:update_self", "advertisement:delete_self"
    ]
}


def has_permission(user: User, permission: str) -> bool:
    if not user or not user.roles:
        return False
    
    for role in user.roles:
        if permission in ROLE_PERMISSIONS.get(role.name, []):
            return True
    return False

def require_permission(permission: str):
    async def dependency(current_user: User = Depends(...)):  # ВАЖНО: Depends(get_current_user) нужно передать в роуте
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    return dependency

def can_manage_user(current_user: User, target_user_id: int) -> bool:
    if not current_user:
        return False
    if has_permission(current_user, "user:delete"):
        return True
    
    if has_permission(current_user, "user:update_self"):
        return current_user.id == target_user_id
    
    return False

def can_manage_advertisement(current_user: User, author_id: int) -> bool:
    if not current_user:
        return False

    if has_permission(current_user, "advertisement:delete"):
        return True
    
    if has_permission(current_user, "advertisement:update_self"):
        return current_user.id == author_id
    
    return False
