from enum import Enum
from poplib import CR
from typing import List
from fastapi import HTTPException, status
from functools import wraps

class Permissions(str, Enum):

    CREATE_DEPARTMENT = "create_department"
    READ_DEPARTMENT = "read_department"
    UPDATE_DEPARTMENT = "update_department"
    DELETE_DEPARTMENT = "delete_department"

    CREATE_ROLE = "create_role"
    READ_ROLE = "read_role"
    UPDATE_ROLE = "update_role"
    DELETE_ROLE = "delete_role"

    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"

    CREATE_CATEGORY = "create_category"
    READ_CATEGORY = "read_category"
    UPDATE_CATEGORY = "update_category"
    DELETE_CATEGORY = "delete_category"
    
    CREATE_IDEA = "create_idea"
    READ_IDEA = "read_idea"
    UPDATE_IDEA = "update_idea"
    DELETE_IDEA = "delete_idea"

class RolePermissions:

    ADMIN = [
        Permissions.CREATE_DEPARTMENT,
        Permissions.READ_DEPARTMENT,
        Permissions.UPDATE_DEPARTMENT,
        Permissions.DELETE_DEPARTMENT,
        Permissions.CREATE_ROLE,
        Permissions.READ_ROLE,
        Permissions.UPDATE_ROLE,
        Permissions.DELETE_ROLE,
        Permissions.CREATE_USER,
        Permissions.READ_USER,
        Permissions.UPDATE_USER,
        Permissions.DELETE_USER,
        Permissions.CREATE_CATEGORY,
        Permissions.READ_CATEGORY,
        Permissions.UPDATE_CATEGORY,
        Permissions.DELETE_CATEGORY,
        Permissions.CREATE_IDEA,
        Permissions.READ_IDEA,
        Permissions.UPDATE_IDEA,
        Permissions.DELETE_IDEA,
    ]

    QA_MANAGER = [
        Permissions.CREATE_DEPARTMENT,
        Permissions.READ_DEPARTMENT,
        Permissions.UPDATE_DEPARTMENT,
        Permissions.DELETE_DEPARTMENT,
        Permissions.CREATE_CATEGORY,
        Permissions.READ_CATEGORY,
        Permissions.UPDATE_CATEGORY,
        Permissions.DELETE_CATEGORY,
    ]

    QA_STAFF = [
        Permissions.READ_DEPARTMENT,
    ]


def has_permission(required_permission: Permissions):

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user = None, **kwargs):
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="User not authenticated"   
            )

            user_role = current_user.role.name

            if user_role == "QA Manager":
                roles_permissions = RolePermissions.QA_MANAGER
            elif user_role == "QA Staff":
                roles_permissions = RolePermissions.QA_STAFF
            else:
                roles_permissions = RolePermissions.ADMIN
            
            if required_permission not in roles_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied"
                )
            
            return await func(*args, current_user = current_user, **kwargs)
        return wrapper
    return decorator