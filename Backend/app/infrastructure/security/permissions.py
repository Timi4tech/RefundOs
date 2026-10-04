from fastapi import Depends, HTTPException, status
from app.domain.enums.user import Role
from app.infrastructure.security.auth import AuthenticatedUser, get_current_user

def require_roles(*roles: Role):
    async def checker(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action.")
        return current_user
    return checker

require_customer = require_roles(Role.CUSTOMER)
require_admin = require_roles(Role.ADMIN)
require_developer = require_roles(Role.DEVELOPER, Role.ADMIN)
