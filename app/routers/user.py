from fastapi import FastAPI, Response, HTTPException, APIRouter, Depends, status
from sqlalchemy.orm import Session
#
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(
    prefix="/user",
    tags=['User']
)

# Post User
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    # Password hash
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
        
    new_user = models.Customer(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# Get Specific User
@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.Customer).filter(models.Customer.customer_id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'Customer With ID {id} Not Found')
    
    return user