from typing import List, Optional
#
from fastapi import FastAPI, Response, HTTPException, APIRouter, Depends, status
from sqlalchemy.orm import Session, joinedload
#
from .. import models, schemas, oauth2
from ..database import get_db

# Organizes and modularizes the application, grouping related routes in a single location
router = APIRouter(
    prefix="/order",
    tags=['Order']
)

# [POST] Sends Order To Restaurant
@router.post("/", response_model=schemas.OrderResponse)
def send_order(order: schemas.OrderSend, db: Session = Depends(get_db),
               current_user: int = Depends(oauth2.get_current_user)):
    
    # Creates a new Purchase model instance associated with the current customer
    new_purchase = models.Purchase(customer_id = current_user.customer_id)
    # Adds this new purchase to the database
    db.add(new_purchase)
    # Commits the transaction
    db.commit()

    # For each product in the order, creates a PurchaseProduct instance associated with the purchase
    for product_id, quantity in order.Products.items():
        
        product = db.query(models.Product).get(product_id)
        
        if product:
            # Creates a PurchaseProduct instance associated with the purchase and product
            new_purchase_product = models.PurchaseProduct(
                purchase_id=new_purchase.purchase_id,
                product_id=product_id,
                quantity=quantity,
                subtotal= product.price * quantity
            )

            # Adds the PurchaseProduct instance to the database
            db.add(new_purchase_product)

    # Commits Changes
    db.commit()

    # Gets purchase updated with product details
    new_purchase = db.query(models.Purchase).get(new_purchase.purchase_id)

    # Creates OrderDetails instances for each item in the order
    order_details = []
    for purchase_product in new_purchase.items:
        order_detail = schemas.OrderDetails(
            name=purchase_product.product.name,
            quantity=purchase_product.quantity,
            subtotal=purchase_product.subtotal
        )
        order_details.append(order_detail)

    # Creates an OrderResponse instance for the response
    order_response = schemas.OrderResponse(
        purchase_id=new_purchase.purchase_id,
        purchase_date=new_purchase.purchase_date,
        status=new_purchase.status,
        items=order_details
    )

    return order_response

# [GET] Requests Customer Order History
@router.get("/all", response_model=List[schemas.OrderResponse])
def get_all_orders(db: Session = Depends(get_db),
                   current_user: int = Depends(oauth2.get_current_user),
                   limit: int = 5, skip: int = 0, search: Optional[str]=""):

    # Defines the query to search for user purchases based on ID and search
    query = (db.query(models.Purchase)
             .filter(models.Purchase.customer_id == current_user.customer_id)
             .filter(models.Purchase.items
                     .any(models.PurchaseProduct.product
                          .has(models.Product.name.ilike(f"%{search}%"))))
             .order_by(models.Purchase.purchase_date.desc())  # Adds ordering by purchase date
             .offset(skip)
             .limit(limit))

    # Gets purchases based on query
    all_purchases = query.all()
    
    # Not found, raises HTTP exception with status 404 (Not Found)
    if not all_purchases:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'You have not placed any orders yet')

    # Creates a list to store request responses
    order_responses = []
        
    for purchase in all_purchases:
        # Creates OrderDetails instances for each item in the order
        order_details = []
        for purchase_product in purchase.items:
            order_detail = schemas.OrderDetails(
                name=purchase_product.product.name,
                quantity=purchase_product.quantity,
                subtotal=purchase_product.subtotal
            )
            order_details.append(order_detail)

        # Creates an OrderResponse instance for each order
        order_response = schemas.OrderResponse(
            purchase_id=purchase.purchase_id,
            purchase_date=purchase.purchase_date,
            status=purchase.status,
            items=order_details
        )

        # Add the OrderResponse instance to the list
        order_responses.append(order_response)
    
    return order_responses

# [GET] Requests Details of a Specific Customer Order (BY ORDER ID)
@router.get("/{id}", response_model=schemas.OrderResponse)
def get_order(id: str, db: Session = Depends(get_db),
              current_user: int = Depends(oauth2.get_current_user)):

    # Queries the database to get the order details with the given ID
    purchase = (db.query(models.Purchase)
                .options(joinedload(models.Purchase.items)
                         .joinedload(models.PurchaseProduct.product))
                .filter(models.Purchase.purchase_id == id)
                .first())
    
    # Not found, raises HTTP exception with status 404 (Not Found)
    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Purchase With ID {id} Not Found')

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
    
    # Creates instances of OrderDetails for each item in the order
    order_details = []
    for purchase_product in purchase.items:
        order_detail = schemas.OrderDetails(
            name=purchase_product.product.name,
            quantity=purchase_product.quantity,
            subtotal=purchase_product.subtotal
        )
        order_details.append(order_detail)

    # Creates an instance of OrderResponse for the response
    order_response = schemas.OrderResponse(
        purchase_id=purchase.purchase_id,
        purchase_date=purchase.purchase_date,
        status=purchase.status,
        items=order_details
    )

    return order_response

# [DELETE] Deletes An Order and Its Related Details - On Delete Cascade (BY ORDER ID)
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(id: str, db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_user)):
    
    # Queries the database to get the user with the given ID
    purchase = db.query(models.Purchase).filter(models.Purchase.purchase_id == id)

    # Not found, raises HTTP exception with status 404 (Not Found)
    if purchase.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Purchase With ID {id} Not Found')
    
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
        
    # Deletes the order from the database based on the provided ID (On Delete Cascade)
    # Synchronize_session=False: used to avoid problems with session synchronization
    purchase.delete(synchronize_session=False)
    # Commits Changes
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# [UPDATE] Updates An Order and Its Related Details (BY ORDER ID)
@router.put("/{id}", response_model=schemas.OrderResponse)
def update_order(id: str, order: schemas.OrderSend, db: Session = Depends(get_db),
                 current_user: int = Depends(oauth2.get_current_user)):
    
    # Queries the database to get the user with the given ID
    purchase = db.query(models.Purchase).get(id)
    
    # Not found, raises HTTP exception with status 404 (Not Found)
    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'Purchase With ID {id} Not Found')
    
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
    
    # Updates the customer ID associated with the order to the currently authenticated customer ID
    purchase.customer_id = current_user.customer_id
    # Commits Changes
    db.commit()
    
    # Deletes all products associated with the order with the provided ID
    # Synchronize_session=False: used to avoid problems with session synchronization
    (db.query(models.PurchaseProduct)
     .filter(models.PurchaseProduct.purchase_id == id)
     .delete(synchronize_session=False))
    # Commits Changes
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
    
    # Commits changes
    db.commit()
    # Gets the updated database order
    updated_purchase = db.query(models.Purchase).get(id)
    
    # Creates instances of OrderDetails for each item in the order
    order_details = []
    for purchase_product in updated_purchase.items:
        order_detail = schemas.OrderDetails(
            name=purchase_product.product.name,
            quantity=purchase_product.quantity,
            subtotal=purchase_product.subtotal
        )
        order_details.append(order_detail)

    # Creates an instance of OrderResponse for the response
    order_response = schemas.OrderResponse(
        purchase_id=updated_purchase.purchase_id,
        purchase_date=updated_purchase.purchase_date,
        status=updated_purchase.status,
        items=order_details
    )

    return order_response