from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    TRACKER_API_URL: str = "https://localhost:8000/api/v1/metrics"


    class Config:
        env_file = ".env"

settings = Settings()