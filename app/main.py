from fastapi import FastAPI, status
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

from .modules import check_cart, find_id, check_id

app = FastAPI()

class Order(BaseModel):
    Main: str
    Drink: str
    Dessert: str
    Additional: Optional[bool] = False
    Spicy: Optional[int] = None

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
def post_cart(cart: Order):
    ID = randrange(0,99999)
    cart_dict = cart.model_dump()
    cache[ID] = cart_dict
    return {"Cart Updated":f'Your Order ID: {ID}'}

# Show Current Cart
@app.get("/cart")
def get_cart():
    cart = check_cart(cache)
    return {"Cart":cart}

# Get Latest Order
@app.get("/cart/latest")
def get_latest_order():
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
    order = check_id(id, cache)
    return order

@app.put("/cart/{id}")
def update_order(id: int, order: Order):
    order = check_id(id, cache)