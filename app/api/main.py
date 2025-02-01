import token
from fastapi import APIRouter

from app.api.routes import (
    user_management,
)

api_router = APIRouter()
api_router.include_router(user_management.router, prefix="/users", tags=["user"])
api_router.include_router(user_management.token_router, prefix="/token", tags=["token"])