from fastapi import FastAPI, status, APIRouter
from .schema.schema import UserResponse,Token,RefreshToken
from .views.user_views import create_user, read_user, read_all_users,login, refresh_token, get_current_user_info

app = FastAPI()

router = APIRouter()

router.add_api_route("/api/users",endpoint=create_user, methods=["POST"], response_model=UserResponse, status_code=status.HTTP_201_CREATED)
router.add_api_route("/api/users/{user_id}",endpoint=read_user, methods=["GET"], response_model=UserResponse)
router.add_api_route("/api/users",endpoint=read_all_users, methods=["GET"])
router.add_api_route("/api/user/login", endpoint=login, methods=["POST"], response_model=Token)
router.add_api_route("/api/token/refresh", endpoint= refresh_token, methods=["POST"], response_model=RefreshToken)
router.add_api_route("/api/user/me", endpoint= get_current_user_info, methods=["GET"], response_model=UserResponse)


app.router.include_router(router)