from app.app import app
from app.config import settings

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.app:app", host=settings.SERVER_HOST, port=settings.SERVER_PORT, reload=True)