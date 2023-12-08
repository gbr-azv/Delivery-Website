from typing import List
#
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
#
from . import models, schemas
from .database import engine, get_db
from .routers import order, user, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

############################## PATHS ##############################

# Get Home Page
@app.get("/")
def home():
    return {"Message":"Welcome to Joe's Restaurant Delivery"}

# Get Menu
@app.get("/menu", response_model=List[schemas.MenuResponse])
def get_menu(db: Session = Depends(get_db)):
    menu = db.query(models.Product).all()
    return menu

app.include_router(order.router)
app.include_router(user.router)
app.include_router(auth.router)