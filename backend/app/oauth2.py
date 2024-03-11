from datetime import datetime, timedelta
#
from jose import JWTError, jwt
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
#
from . import schemas, models
from .database import get_db
from .config import settings

# Defines an OAuth2 scheme for authentication with passwords 
# Specifies the endpoint for obtaining the token, which is '/login'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# Constants used to create and verify JWT tokens
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Creates a JWT token based on the given data
def create_access_token(data: dict):
    
    # Creates a copy of the provided data
    to_encode = data.copy()
    
    # Calculates the token expiration time (Add a time range)
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Updates the data to be encoded, including the calculated expiration time
    to_encode.update({"exp":expire})
    
    # Uses the jwt library to ENCODE data using the "SECRET_KEY" "ALGORITHM"
    # The result is an encoded JWT token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

# Verifies and decodes a JWT token to obtain information associated with it
def verify_access_token(token: str, credentials_exception):
    
    try: 
        
        # Uses the jwt library to DECODE data using the "SECRET_KEY" "ALGORITHM"
        # The result is a dictionary that contains the information contained in the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Gets the value associated with the dictionary key "customer_id"
        id: str = payload.get("customer_id")
        
        # Checks whether the "customer_id" field is present in the payload
        # If not, throw an HTTP 401 (Unauthorized) exception
        if id is None:
            raise credentials_exception
        
        # Creates an instance of "schemas.TokenData" with the ID extracted from the token
        token_data = schemas.TokenData(id=id)
    
    # Catches exceptions of the JWTError class that may occur during the token decoding process
    except JWTError:
        raise credentials_exception
    
    return token_data

# FastAPI dependency used to get the current user based on the provided JWT token
# token: str = Depends(oauth2_scheme): the token is extracted from the authorization header of the HTTP request
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    
    # Creates an HTTPException instance that will be thrown if credential validation fails
    # Headers: the authentication is done via "Bearer" (standard for JWT tokens)
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f'Could Not Validate Credentials',
                                          headers={"WWW-Authenticate":"Bearer"})
    
    # Uses the verify_access_token function to verify and decode the JWT token
    # If the check fails, this line will raise the exception specified by credentials_exception
    token = verify_access_token(token, credentials_exception)
    
    # Uses the database session instance to query the database for the user associated 
    # with the identification (id) extracted from the token
    user = db.query(models.Customer).filter(models.Customer.customer_id == token.id).first()
    
    return user