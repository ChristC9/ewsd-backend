from fastapi import APIRouter
from app.api.routes import (
    user_management,
    roles,
    departments,
    ideas,
    categories,
    comments,
    like,
    dashboard,
)

api_router = APIRouter()
api_router.include_router(user_management.router, prefix="/users", tags=["User Management"])
api_router.include_router(user_management.token_router, prefix="/token", tags=["Token Management"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles Management"])
api_router.include_router(ideas.router, prefix="/ideas", tags=["Ideas Management"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard Management"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories Management"])
api_router.include_router(departments.router, prefix="/departments", tags=["Departments Management"])
api_router.include_router(comments.router, prefix="/comments", tags=["Comments Management"])
api_router.include_router(like.router, prefix="/likes", tags=["Likes Management"])