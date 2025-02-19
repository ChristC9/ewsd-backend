from datetime import timedelta
from ..auth.authentication import create_token
from ..models.user_model import User
from ..config import settings

access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

def get_access_token(user: User):
    access_token_expires = timedelta(minutes= access_token_expire_minutes)
    access_token = create_token(

        data = {
            "sub": user.username, 
            "email": user.email,
            "role": user.role.name,
            "type": "access"
        },
        expires_delta = access_token_expires
    )
    return access_token


def get_refresh_token(user: User):

    refresh_token_expires = timedelta(days= refresh_token_expire_days)
    refresh_token = create_token(

        data = {

            "sub": user.username,
            "type": "refresh"
        },
        expires_delta = refresh_token_expires   
    )
    return refresh_token