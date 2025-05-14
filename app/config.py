import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    DATABASE_HOSTNAME: str = os.getenv("DATABASE_HOSTNAME", "localhost")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5432")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "password")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "socialmedia")
    DATABASE_USERNAME: str = os.getenv("DATABASE_USERNAME", "postgres")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key_here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()