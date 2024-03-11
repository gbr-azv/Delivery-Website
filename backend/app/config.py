'''This file is intended to store values of the app's environment variables'''
'''From the Settings class, which automatically loads the environment variables defined in the class
from the ".env file" (as configured in the Config class).'''

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOSTNAME: str
    DB_PORT: str 
    DB_PASSWORD: str 
    DB_NAME: str
    DB_USERNAME: str 
    JWT_ALGORITHM: str 
    ACCESS_TOKEN_EXPIRES_MINUTES: int
    REFRESH_TOKEN_EXPIRES_MINUTES: int
    PRIVATE_KEY: str
    PUBLIC_KEY: str
    CLIENT_ORIGIN: str
    SECRET_KEY: str
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
     
    class Config:
        env_file = ".env"

settings = Settings()