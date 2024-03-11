from fastapi import FastAPI, Response, HTTPException, APIRouter, Depends, status
from sqlalchemy.orm import Session
#
from .. import models, schemas, utils, oauth2
from ..database import get_db

# Organizes and modularizes the application, grouping related routes in a single location
router = APIRouter(
    prefix="/user",
    tags=['User']
)

# [GET] Gets Personal Data From User's Own Account
@router.get("/", response_model=schemas.UserDetails)
def get_user(db: Session = Depends(get_db),
             current_user: int = Depends(oauth2.get_current_user)):
    
    # Queries the database to get the user with the given ID
    user = db.query(models.Customer).filter(models.Customer.customer_id == current_user.customer_id).first()
    
    return user

# [DELETE] Deletes Own Account
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    
    # Deletes the user from the database based on the provided ID (On Delete Cascade)
    # Synchronize_session=False: used to avoid problems with session synchronization
    (db.query(models.Customer)
     .filter(models.Customer.customer_id == current_user.customer_id)
     .delete(synchronize_session=False))
    
    # Commits the transaction to the database, making the deletion permanent
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# [UPDATE] Updates Personal Data From The User's Own Account
@router.put("/", response_model=schemas.UserResponse)
def update_user(updated_user: schemas.UserUpdate, db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_user)):
    
    # Queries the database to get the user with the given ID
    user_query = (db.query(models.Customer)
                  .filter(models.Customer.customer_id == current_user.customer_id))
    
    # Gets the query user
    user = user_query.first()
        
    # Updates the user from the database based on the provided ID
    # Synchronize_session=False: used to avoid problems with session synchronization
    user_query.update(updated_user.model_dump(), synchronize_session=False)
    db.commit()
    
    return user