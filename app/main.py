from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

from .modules import check_cart, find_id

app = FastAPI()

class Menu(BaseModel):
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
    return{"Menu":menu}

# Add To Cart
@app.post("/cart")
def post_cart(cart: Menu):
    ID = randrange(0,99999)
    cart_dict = cart.model_dump()
    cache[ID] = cart_dict
    return{"Cart Updated":cache}

# Show Current Cart
@app.get("/cart")
def get_cart():
    cart = check_cart(cache)
    return {"Response":cart}

# Show Specific Order
@app.get("/cart/{id}")
def get_order(id):
    order = find_id(int(id),cache)
    return {"Response":order}