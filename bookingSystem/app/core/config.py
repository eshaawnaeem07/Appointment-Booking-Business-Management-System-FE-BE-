from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env", override=True)


class Settings(BaseSettings):
    SENDGRID_API_KEY: str
    SQLALCHEMY_DATABASE_URL: str
    FROM_EMAIL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

settings = Settings()

SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_EXPIRE_DAYS = 7
REFRESH_SECRET_KEY = "my-super-secret-refresh-token-key"

