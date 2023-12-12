from typing import List
#
from fastapi import FastAPI, Response, HTTPException, APIRouter, Depends, status
from sqlalchemy.orm import Session, class_mapper
#
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/order",
    tags=['Order']
)

# Post Order
@router.post("/", response_model=schemas.OrderResponse)
def send_order(order: schemas.OrderSend, db: Session = Depends(get_db),
               current_user: int = Depends(oauth2.get_current_user)):
    
    new_purchase = models.Purchase(customer_id = current_user.customer_id)
    db.add(new_purchase)
    db.commit()
    new_purchase = db.query(models.Purchase).get(new_purchase.purchase_id)

    for product_id, quantity in order.Products.items():
        product = db.query(models.Product).get(product_id)
        if product:
            new_purchase_product = models.PurchaseProduct(
                purchase_id=new_purchase.purchase_id,
                product_id=product_id,
                quantity=quantity,
                subtotal=product.price * quantity
            )
            db.add(new_purchase_product)
            
    db.commit()
    purchase_dict = {column.key: getattr(new_purchase, column.key) 
                     for column in class_mapper(models.Purchase).columns}
    
    return purchase_dict

# Get Customer All Orders
@router.get("/all/{id}", response_model=List[schemas.OrderResponse])
def get_all_orders(id: int, db: Session = Depends(get_db),
                   current_user: int = Depends(oauth2.get_current_user)):
    
    if current_user.customer_id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Unauthorized')
    
    all_purchases = (db.query(models.Purchase)
                     .filter(models.Purchase.customer_id == id).all())
    
    if not all_purchases:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Customer With ID {id} Not Found')
        
    return all_purchases

# Get Specific Order
@router.get("/{id}", response_model=List[schemas.OrderDetails])
def get_order(id: int, db: Session = Depends(get_db),
              current_user: int = Depends(oauth2.get_current_user)):
    
    validation = (db.query(models.Purchase)
              .join(models.Customer)
              .filter(models.Purchase.purchase_id == id)
              .filter(models.Customer.customer_id == current_user.customer_id)
              .first())
    
    if not validation:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Unauthorized')
    
    purchase = (db.query(models.PurchaseProduct)
                .filter(models.PurchaseProduct.purchase_id == id).all())
    
    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Purchase With ID {id} Not Found')
        
    return purchase

# Delete Specific Order
@router.delete("/{id}")
def delete_order(id: int, db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_user)):
    
    validation = (db.query(models.Purchase)
              .join(models.Customer)
              .filter(models.Purchase.purchase_id == id)
              .filter(models.Customer.customer_id == current_user.customer_id)
              .first())
    
    if not validation:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Unauthorized')
    
    purchase = db.query(models.Purchase).filter(models.Purchase.purchase_id == id)
    
    purchase_product = (db.query(models.PurchaseProduct)
                        .filter(models.PurchaseProduct.purchase_id == id))
    
    if purchase.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Purchase With ID {id} Not Found')
        
    purchase_product.delete(synchronize_session=False)
    purchase.delete(synchronize_session=False)
    db.commit()
    
    return {"Success":f'Purchase With ID {id} Deleted'}

# Update Specific Order
@router.put("/{id}", response_model=schemas.OrderResponse)
def update_order(id: int, order: schemas.OrderSend, db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_user)):
    
    validation = (db.query(models.Purchase)
              .join(models.Customer)
              .filter(models.Purchase.purchase_id == id)
              .filter(models.Customer.customer_id == current_user.customer_id)
              .first())
    
    if not validation:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Unauthorized')
    
    purchase = db.query(models.Purchase).get(id)
    
    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'Purchase With ID {id} Not Found')
        
    purchase.customer_id = current_user.customer_id
    db.commit()
    
    (db.query(models.PurchaseProduct)
     .filter(models.PurchaseProduct.purchase_id == id)
     .delete(synchronize_session=False))
    db.commit()

    for product_id, quantity in order.Products.items():
        product = db.query(models.Product).get(product_id)
        if product:
            new_purchase_product = models.PurchaseProduct(
                purchase_id=id,
                product_id=product_id,
                quantity=quantity,
                subtotal=product.price * quantity
            )
            db.add(new_purchase_product)
            
    db.commit()
    updated_purchase = db.query(models.Purchase).get(id)
    
    purchase_dict = {column.key: getattr(updated_purchase, column.key) 
                     for column in class_mapper(models.Purchase).columns}
    
    return purchase_dict