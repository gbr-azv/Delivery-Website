from base64 import b64decode
from typing import List
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from .config import settings

class Settings(BaseModel):
    authjwt_algorithm: str = settings.JWT_ALGORITHM
    authjwt_decode_algorithms: List[str] = [settings.JWT_ALGORITHM]
    authjwt_token_location: set = {'cookies', 'headers'}
    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_cookie_csrf_protect: bool = False
    authjwt_public_key: str = b64decode(settings.PRIVATE_KEY).decode('utf-8')

@AuthJWT.load_config
def get_config():
    return Settings()