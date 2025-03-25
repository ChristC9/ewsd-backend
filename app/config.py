from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME : str
    API_STR : str
    SECRET_KEY : str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int
    REFRESH_TOKEN_EXPIRE_DAYS : int
    DB_USER : str
    DB_PASSWORD : str
    DB_NAME : str
    DB_HOST : str
    DB_PORT : int
    SERVER_HOST : str
    SERVER_PORT : int
    OTP_EXPIRE_MINUTES : int
    SENDGRID_API_KEY : str

    
    @property
    def db_url(self):
        return (
                    f"postgresql+asyncpg://{self.DB_USER}:"
                    f"{self.DB_PASSWORD}@"
                    f"{self.DB_HOST}:{self.DB_PORT}/"
                    f"{self.DB_NAME}"
                )
    
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

@lru_cache
def get_settings():
    return Settings()


settings = get_settings()