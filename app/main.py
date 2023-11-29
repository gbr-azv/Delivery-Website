from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()

class Menu(BaseModel):
    Main: str
    Drink: str
    Dessert: str
    Additional: bool = False
    Spicy: Optional[int] = None

# Remaining Cart's Selection
cache = [{"Main":"X-Salad", "Drink": "Soda", "Dessert":"Ice Cream", "Additional":True, "Spicy":5, "id":12345},
      {"Main":"Chicken Burguer", "Drink": "Milk", "Dessert":"Milkshake", "Additional":True, "Spicy":10, "id":13567}]

# Menu
menu = [{"Main":["X-Salad", "Chicken Burguer", "Double Cheese Burguer"]},
        {"Drinks":["Soda", "Milk", "Orange Juice"]},
        {"Desserts":["Ice Cream", "Milkshake", "Donuts"]}]

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
    cart_dict = cart.model_dump()
    cart_dict["id"] = randrange(0,99999)
    cache.append(cart_dict)
    return{"Cart":cart_dict}

# Show Current Cart
@app.get("/cart")
def get_cart():
    return{"Cart":cache}

# Show specific order
@app.get("/cart/{id}")
def get_order(id):
    return {id:"Here is your order"}