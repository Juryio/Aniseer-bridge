from functools import lru_cache
from pydantic_settings import BaseSettings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Settings(BaseSettings):
    jellyseerr_url: str
    jellyseerr_api_key: str
    download_path: str = "/data/anime"
    poll_interval: int = 60
    web_port: int = 8081
    database_url: str = "sqlite:///./jellyseerr_aniworld_bridge.db"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
