from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    HOST : str
    PORT : int
    PASSWORD : str

    model_config = SettingsConfigDict(env_file='.env')

@lru_cache()
def get_settings():
    return Settings()