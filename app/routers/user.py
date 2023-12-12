from fastapi import FastAPI, Response, HTTPException, APIRouter, Depends, status
from sqlalchemy.orm import Session
#
from .. import models, schemas, utils, oauth2
from ..database import get_db

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
        
    new_user = models.Customer(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# [GET] Get Personal Data From User's Own Account
@router.get("/{id}", response_model=schemas.UserDetails)
def get_user(id: int, db: Session = Depends(get_db),
             current_user: int = Depends(oauth2.get_current_user)):
    
    if current_user.customer_id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Unauthorized')
    
    user = db.query(models.Customer).filter(models.Customer.customer_id == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'Customer With ID {id} Not Found')
    
    return user

# [DELETE] Delete Own Account
@router.delete("/{id}")
def delete_user(id: int, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    
    if current_user.customer_id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Unauthorized')
    
    user = (db.query(models.Customer)
            .filter(models.Customer.customer_id == id))
       
    if user.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Customer With ID {id} Not Found')
    
    purchases = (db.query(models.Purchase)
                 .filter(models.Purchase.customer_id == id).all())
        
    for purchase in purchases:
        (db.query(models.PurchaseProduct)
         .filter(models.PurchaseProduct.purchase_id == purchase.purchase_id)
         .delete(synchronize_session=False))

    (db.query(models.Purchase)
     .filter(models.Purchase.customer_id == id)
     .delete(synchronize_session=False))
    
    (db.query(models.Customer)
     .filter(models.Customer.customer_id == id)
     .delete(synchronize_session=False))
    
    db.commit()
    
    return {"Success":f'Customer With ID {id} Deleted'}

# [UPDATE] Update Personal Data From The User's Own Account
@router.put("/{id}", response_model=schemas.UserResponse)
def update_user(id: int, updated_user: schemas.UserUpdate, db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_user)):
    
    if current_user.customer_id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Unauthorized')
    
    user_query = (db.query(models.Customer)
                  .filter(models.Customer.customer_id == id))
    
    user = user_query.first()
    
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'User With ID {id} Not Found')
    
    user_query.update(updated_user.model_dump(), synchronize_session=False)
    db.commit()
    
    return user