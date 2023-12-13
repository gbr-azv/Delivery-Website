from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
#
from .. import schemas, models, utils, oauth2
from ..database import get_db

# Organizes and modularizes the application, grouping related routes in a single location
router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    
    # The function's parameters include the user credentials provided 
    # in the request body (user_credentials) and the database session.
    user = (db.query(models.Customer)
            .filter(models.Customer.email == user_credentials.username).first())
    
    # If the user is not found, it raises an HTTP exception with status 403 (Forbidden)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentials')
    
    # Checks if the provided password (user_credentials.password) 
    # matches the password stored in the database
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentials')
    
    # Creates an access token using the create_access_token function defined in the oauth2 object.
    # This access token is based on the data provided
    # Which in this case include the customer ID (user.customer_id)
    access_token = oauth2.create_access_token(data={"customer_id":user.customer_id})
    
    return {"access_token" : access_token, "token_type":"bearer"}