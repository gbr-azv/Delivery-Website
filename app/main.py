from fastapi import FastAPI, status
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

from .modules import check_cart, find_id, check_id

app = FastAPI()

class Order(BaseModel):
    Main: Optional[str] = None
    Drink: Optional[str] = None
    Dessert: Optional[str] = None
    Additional: Optional[bool] = False
    Spicy: Optional[int] = None
    
# Trying Connection With DB
while True:
    try:
        conn = psycopg2.connect(host='localhost', database='FastAPI', user='postgres', password='e3rxapap', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('Database connection was succesfull')
        break
    except Exception as error:
        print("Connecting to database failed ;(")
        time.sleep(2)
    
# Remaining Cart's Selection
cache = {}

# Menu
menu = {"Main":["X-Salad", "Chicken Burguer", "Double Cheese Burguer"],
        "Drinks":["Soda", "Milk", "Orange Juice"],
        "Desserts":["Ice Cream", "Milkshake", "Donuts"]}

# Root
@app.get("/")
def home():
    return {"Message":"Welcome to Joe's Restaurant Menu"}

# Menu
@app.get("/menu")
def get_menu():
    return {"Menu":menu}

# Add To Cart
@app.post("/cart", status_code=status.HTTP_200_OK)
def post_order(order: Order):
    ID = randrange(0,99999)
    order_dict = order.model_dump()
    cache[ID] = order_dict
    return {"Order Dispatched":f'Your Order ID: {ID}'}

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