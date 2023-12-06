from typing import Optional
from random import randrange
import time

from fastapi import FastAPI, status, Depends
from fastapi.params import Body
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session
from sqlalchemy.orm import class_mapper

from .modules import check_cart, find_id, check_id

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Order(BaseModel):
    Customer_id: int
    Products: dict[int, int]
    
# Trying Connection With DB
while True:
    try:
        conn = psycopg2.connect(host='localhost', database='FastAPI', user='postgres', password='e3rxapap', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was succesful")
        break
    except Exception as error:
        print("Connecting to database failed")
        time.sleep(2)
    
# Remaining Cart's Selection
cache = {}

# Root
@app.get("/")
def home():
    return {"Message":"Welcome to Joe's Restaurant Menu"}

# Menu
@app.get("/menu")
def get_menu(db: Session = Depends(get_db)):
    menu = db.query(models.Product).all()
    return {"Menu":menu}

# Send Order
@app.post("/order", status_code=status.HTTP_200_OK)
def post_order(order: Order, db: Session = Depends(get_db)):
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
    purchase_dict = {column.key: getattr(new_purchase, column.key) for column in class_mapper(models.Purchase).columns}
    return {"Order Dispatched":purchase_dict}

# Show Current Cart
@app.get("/cart")
def get_cart():
    cart = check_cart(cache)
    return cart

# Get Latest Order
@app.get("/cart/latest")
def get_latest_order():
    if len(cache) == 0:
        response = f'Your cart is empty'
        return {"Cart":response}
    id = list(cache.keys())[-1]
    latest = cache[id]
    return {"Order":latest}

# Show Specific Order
@app.get("/cart/{id}")
def get_order(id: int):
    order = find_id(id,cache)
    return order

# Delete Specific Order
@app.delete("/cart/{id}")
def delete_order(id: int):
    response = check_id(id, cache)
    if response == True:
        del cache[id]
        return {"Cart Updated":f'Your Deleted Order ID: {id}'}
    return response

# Update Specific Order
@app.put("/cart/{id}")
def update_order(id: int, order: Order):
    response = check_id(id, cache)
    if response == True:
        order_dict = order.model_dump()
        cache[id] = order_dict
        return {"Order Updated":f'Your Updated Order ID: {id}'}
    return response