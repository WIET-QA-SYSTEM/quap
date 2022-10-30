import os
from pathlib import Path

from dotenv import load_dotenv


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str = "quap"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = ""

    REDIS_HOST: str = os.environ["REDIS_HOST"]
    REDIS_PORT: str = os.environ["REDIS_PORT"]

    POSTGRES_HOST: str = os.environ["POSTGRES_HOST"]
    POSTGRES_PORT: str = os.environ["POSTGRES_PORT"]
    POSTGRES_DB: str = os.environ["POSTGRES_DB"]
    POSTGRES_USER: str = os.environ["POSTGRES_USER"]
    POSTGRES_PASSWORD: str = os.environ["POSTGRES_PASSWORD"]

    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


settings = Settings()
