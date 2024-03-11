from typing import List
#
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
#
from . import models, schemas
from .database import engine, get_db
from .routers import order, user, auth
from .seed import insert_initial_data

# Called to create the tables in the database based on the defined models
models.Base.metadata.create_all(bind=engine)

# Inserts the restaurant menu, when the first time the database tables are initialized
insert_initial_data()

# Creates an instance of the FastAPI application
app = FastAPI()

# Defines a list of origins allowed
origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost:8000",
    "https://localhost:8000",
]

# Implement CORS in the application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

############################## ROUTES ##############################

# [GET] Requests The Restaurant's Home Page
@app.get("/")
def home():
    return {"Message":"Welcome to Joe's Restaurant Delivery"}

# [GET] Requests The Restaurant Menu
@app.get("/menu", response_model=List[schemas.MenuResponse])
def get_menu(db: Session = Depends(get_db)):
    menu = db.query(models.Product).all()
    return menu

# Includes routes from another router, in the main application
# Which are in: "routers/order.py", "routers/user.py", and "routers/auth.py"'
# Useful for organizing and modularizing routes in different parts of the code
app.include_router(order.router)
app.include_router(user.router)
app.include_router(auth.router)