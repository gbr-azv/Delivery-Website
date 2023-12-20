'''This file is intended to store values of the app's environment variables'''
'''From the Settings class, which automatically loads the environment variables defined in the class
from the ".env file" (as configured in the Config class).'''

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str 
    DATABASE_PASSWORD: str 
    DATABASE_NAME: str
    DATABASE_USERNAME: str 
    SECRET_KEY: str
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
     
    class Config:
        env_file = ".env"

settings = Settings()