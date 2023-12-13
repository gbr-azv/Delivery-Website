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

# [POST] Create User
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    # Password Hash
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    # Creates new instance, unpacks values and commits
    new_user = models.Customer(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# [GET] Get Personal Data From User's Own Account (BY USER ID)
@router.get("/{id}", response_model=schemas.UserDetails)
def get_user(id: int, db: Session = Depends(get_db),
             current_user: int = Depends(oauth2.get_current_user)):
    
    # Checks if the ID of the current authenticated user is different 
    # from the ID provided in the request
    if current_user.customer_id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Unauthorized')
    
    # Queries the database to get the user with the given ID
    user = db.query(models.Customer).filter(models.Customer.customer_id == id).first()
    
    # Not found, raises HTTP exception with status 404 (Not Found)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'Customer With ID {id} Not Found')
    
    return user

# [DELETE] Delete Own Account (BY USER ID)
@router.delete("/{id}")
def delete_user(id: int, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    
    # Checks if the ID of the current authenticated user is different 
    # from the ID provided in the request
    if current_user.customer_id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Unauthorized')
    
    # Queries the database to get the user with the given ID
    user = (db.query(models.Customer)
            .filter(models.Customer.customer_id == id))
    
    # Not found, raises HTTP exception with status 404 (Not Found)
    if user.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Customer With ID {id} Not Found')
    
    # Deletes the user from the database based on the provided ID (On Delete Cascade)
    # Synchronize_session=False: used to avoid problems with session synchronization
    (db.query(models.Customer)
     .filter(models.Customer.customer_id == id)
     .delete(synchronize_session=False))
    
    # Commits the transaction to the database, making the deletion permanent
    db.commit()
    
    return {"Success":f'Customer With ID {id} Deleted'}

# [UPDATE] Update Personal Data From The User's Own Account (BY USER ID)
@router.put("/{id}", response_model=schemas.UserResponse)
def update_user(id: int, updated_user: schemas.UserUpdate, db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_user)):
    
    # Checks if the ID of the current authenticated user is different 
    # from the ID provided in the request
    if current_user.customer_id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Unauthorized')
    
    # Queries the database to get the user with the given ID
    user_query = (db.query(models.Customer)
                  .filter(models.Customer.customer_id == id))
    
    # Gets the query user
    user = user_query.first()
    
    # Not found, raises HTTP exception with status 404 (Not Found)
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'User With ID {id} Not Found')
        
    # Updates the user from the database based on the provided ID
    # Synchronize_session=False: used to avoid problems with session synchronization
    user_query.update(updated_user.model_dump(), synchronize_session=False)
    db.commit()
    
    return user