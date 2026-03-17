from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    COLLECTION_NAME: str = "docuchat_docs"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    UPLOAD_DIR: str = "/app/uploads"

    MAX_UPLOAD_SIZE_MB: int = 10

    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    LLM_KEY : str = ""
    DAILY_TOKEN_LIMIT: int = 70000

    ALLOWED_ORIGINS: str = "http://frontend:80"

    class Config:
        env_file = ".env"

settings = Settings()
