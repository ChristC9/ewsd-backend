import token
from fastapi import APIRouter

from app.api.routes import (
    user_management,
    roles,
    departments
)

api_router = APIRouter()
api_router.include_router(user_management.router, prefix="/users", tags=["User Management"])
api_router.include_router(user_management.token_router, prefix="/token", tags=["Token Management"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles Management"])
api_router.include_router(departments.router, prefix="/departments", tags=["Departments Management"])