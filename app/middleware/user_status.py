from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.database import get_db, AsyncSessionLocal
from app.repositories.users import UserRepository

class UserStatusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to invalidate sessions for disabled users.
    This checks if the authenticated user has been disabled and rejects requests if they are.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip middleware for authentication routes
        if request.url.path == "/api/users/login" or request.url.path == "/api/users/refresh-token":
            return await call_next(request)
            
        # Get the authorization header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return await call_next(request)
            
        # Extract the token
        token = authorization.replace("Bearer ", "")
        
        try:
            # Decode the token without verifying signature first to get the username
            # This is just to extract the subject claim
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            username = payload.get("sub")
            
            if not username:
                return await call_next(request)
                
            # Get a async database 
            # Check if user is disabled
            async with AsyncSessionLocal() as db:
                user_repo = UserRepository(db)
                user = await user_repo.get_user(username=username)
            
                if user and not user.is_active:
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={
                            "detail": "User account is disabled. Session invalidated."
                        },
                        headers={"WWW-Authenticate": "Bearer"}
                    )

        except JWTError:
            # If token is invalid, let the request handlers deal with it
            pass
        
        # Continue with the request if user is not disabled
        return await call_next(request)