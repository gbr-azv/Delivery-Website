from fastapi import FastAPI, status, Depends, HTTPException
from pydantic import BaseModel
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy.orm import class_mapper

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Order(BaseModel):
    Customer_id: int
    Products: dict[int, int]

# Get Home Page
@app.get("/")
def home():
    return {"Message":"Welcome to Joe's Restaurant Menu"}

# Get Menu
@app.get("/menu")
def get_menu(db: Session = Depends(get_db)):
    menu = db.query(models.Product).all()
    return {"Menu":menu}

# Post Order
@app.post("/send_order", status_code=status.HTTP_200_OK)
def send_order(order: Order, db: Session = Depends(get_db)):
    new_purchase = models.Purchase(customer_id = order.Customer_id)
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
    return {"Order Dispatched":purchase_dict}

# Get Customer All Orders
@app.get("/all_orders/{id}")
def get_all_orders(id: int, db: Session = Depends(get_db)):
    all_purchases = (db.query(models.Purchase)
                     .filter(models.Purchase.customer_id == id).all())
    if not all_purchases:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Customer With ID {id} Not Found')
    return {"Your Orders":all_purchases}

# Get Specific Order
@app.get("/order/{id}")
def get_order(id: int, db: Session = Depends(get_db)):
    purchase = (db.query(models.PurchaseProduct)
                .filter(models.PurchaseProduct.purchase_id == id).all())
    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Purchase With ID {id} Not Found')
    return {"Your Order Details":purchase}

# Delete Specific Order
@app.delete("/order/{id}")
def delete_order(id: int, db: Session = Depends(get_db)):
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
@app.put("/order/{id}")
def update_order(id: int, order: Order, db: Session = Depends(get_db)):
    purchase = db.query(models.Purchase).get(id)
    if not purchase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'Purchase With ID {id} Not Found')
    purchase.customer_id = order.Customer_id
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
    return {"Order Updated": purchase_dict}