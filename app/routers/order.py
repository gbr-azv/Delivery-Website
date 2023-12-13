from typing import List
#
from fastapi import FastAPI, Response, HTTPException, APIRouter, Depends, status
from sqlalchemy.orm import Session, class_mapper
#
from .. import models, schemas, oauth2
from ..database import get_db

# Organizes and modularizes the application, grouping related routes in a single location
router = APIRouter(
    prefix="/order",
    tags=['Order']
)

# [POST] Send Order To Restaurant
@router.post("/", response_model=schemas.OrderResponse)
def send_order(order: schemas.OrderSend, db: Session = Depends(get_db),
               current_user: int = Depends(oauth2.get_current_user)):
    
    # Creates a new Purchase model instance associated with the current customer
    # Add this new purchase to the database
    # Commits the transaction
    # Get updated status
    new_purchase = models.Purchase(customer_id = current_user.customer_id)
    db.add(new_purchase)
    db.commit()
    new_purchase = db.query(models.Purchase).get(new_purchase.purchase_id)

    # Iterates over the items in the order (order.Products)
    for product_id, quantity in order.Products.items():
        product = db.query(models.Product).get(product_id)
        # For each product in the order, checks whether the product exists in the database
        if product:
            # Creates new instances of the PurchaseProduct model associated with the new order (id)
            new_purchase_product = models.PurchaseProduct(
                purchase_id=new_purchase.purchase_id,
                product_id=product_id,
                quantity=quantity,
                subtotal=product.price * quantity
            )
            # Adds this new product entry to the database
            db.add(new_purchase_product)
    
    # Commit changes
    db.commit()
    
    # Creates a dictionary containing the details of the newly created purchase
    # to build the response to the request
    purchase_dict = {column.key: getattr(new_purchase, column.key) 
                     for column in class_mapper(models.Purchase).columns}
    
    return purchase_dict

# [GET] Requests Customer Order History (BY USER ID)
@router.get("/all/{id}", response_model=List[schemas.OrderResponse])
def get_all_orders(id: int, db: Session = Depends(get_db),
                   current_user: int = Depends(oauth2.get_current_user)):

    # Checks if the ID of the current authenticated user is different 
    # from the ID provided in the request
    if current_user.customer_id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Unauthorized')
        
    # Queries the database to get the user with the given ID
    all_purchases = (db.query(models.Purchase)
                     .filter(models.Purchase.customer_id == id).all())
    
    # Not found, raises HTTP exception with status 404 (Not Found)
    if not all_purchases:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Customer With ID {id} Not Found')
        
    return all_purchases

# [GET] Requests Details of a Specific Customer Order (BY ORDER ID)
@router.get("/{id}", response_model=List[schemas.OrderDetails])
def get_order(id: int, db: Session = Depends(get_db),
              current_user: int = Depends(oauth2.get_current_user)):

    # Checks whether the order with the provided ID belongs to the currently authenticated customer
    # The query joins the Purchase and Customer tables and applies filters
    # to ensure the order belongs to the authenticated customer
    validation = (db.query(models.Purchase)
              .join(models.Customer)
              .filter(models.Purchase.purchase_id == id)
              .filter(models.Customer.customer_id == current_user.customer_id)
              .first())

    # Checks if the validation (previous query result) is false
    if not validation:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Unauthorized')
    
    # Queries the database to get the user with the given ID
    purchase = (db.query(models.PurchaseProduct)
                .filter(models.PurchaseProduct.purchase_id == id).all())
    
    # Not found, raises HTTP exception with status 404 (Not Found)
    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Purchase With ID {id} Not Found')
        
    return purchase

# [DELETE] Delete An Order and Its Related Details - On Delete Cascade (BY ORDER ID)
@router.delete("/{id}")
def delete_order(id: int, db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_user)):
    
    # Checks whether the order with the provided ID belongs to the currently authenticated customer
    # The query joins the Purchase and Customer tables and applies filters
    # to ensure the order belongs to the authenticated customer
    validation = (db.query(models.Purchase)
              .join(models.Customer)
              .filter(models.Purchase.purchase_id == id)
              .filter(models.Customer.customer_id == current_user.customer_id)
              .first())
    
    # Checks if the validation (previous query result) is false
    if not validation:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Unauthorized')
    
    # Queries the database to get the user with the given ID
    purchase = db.query(models.Purchase).filter(models.Purchase.purchase_id == id)

    # Not found, raises HTTP exception with status 404 (Not Found)
    if purchase.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Purchase With ID {id} Not Found')
        
    # Deletes the order from the database based on the provided ID (On Delete Cascade)
    # Synchronize_session=False: used to avoid problems with session synchronization
    purchase.delete(synchronize_session=False)
    db.commit()
    
    return {"Success":f'Purchase With ID {id} Deleted'}

# Update Specific Order
@router.put("/{id}", response_model=schemas.OrderResponse)
def update_order(id: int, order: schemas.OrderSend, db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_user)):
    
    # Checks whether the order with the provided ID belongs to the currently authenticated customer
    # The query joins the Purchase and Customer tables and applies filters
    # to ensure the order belongs to the authenticated customer
    validation = (db.query(models.Purchase)
              .join(models.Customer)
              .filter(models.Purchase.purchase_id == id)
              .filter(models.Customer.customer_id == current_user.customer_id)
              .first())
    
    # Checks if the validation (previous query result) is false
    if not validation:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Unauthorized')
    
    # Queries the database to get the user with the given ID
    purchase = db.query(models.Purchase).get(id)
    
    # Not found, raises HTTP exception with status 404 (Not Found)
    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'Purchase With ID {id} Not Found')
    
    # Updates the customer ID associated with the order to the currently authenticated customer ID
    purchase.customer_id = current_user.customer_id
    db.commit()
    
    # Deletes all products associated with the order with the provided ID
    # Synchronize_session=False: used to avoid problems with session synchronization
    (db.query(models.PurchaseProduct)
     .filter(models.PurchaseProduct.purchase_id == id)
     .delete(synchronize_session=False))
    db.commit()

    # Iterates over the products in the order (order.Products)
    for product_id, quantity in order.Products.items():
        product = db.query(models.Product).get(product_id)
        # For each product in the order, checks whether the product exists in the database
        if product:
            # Creates new instances of the PurchaseProduct model associated with the updated order (id)
            new_purchase_product = models.PurchaseProduct(
                purchase_id=id,
                product_id=product_id,
                quantity=quantity,
                subtotal=product.price * quantity
            )
            # Adds this new product entry to the database
            db.add(new_purchase_product)
    
    # Commit changes
    # Gets the updated database order
    db.commit()
    updated_purchase = db.query(models.Purchase).get(id)
    
    # Creates a dictionary containing the details of the newly updated purchase
    # to build the response to the request
    purchase_dict = {column.key: getattr(updated_purchase, column.key) 
                     for column in class_mapper(models.Purchase).columns}
    
    return purchase_dict