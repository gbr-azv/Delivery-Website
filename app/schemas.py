from datetime import datetime
from pydantic import BaseModel, EmailStr

############################## ORDER ##############################

class OrderSend(BaseModel):
    Customer_id: int
    Products: dict[int, int]

class MenuResponse(BaseModel):
    name: str
    description: str
    price: float
    product_id: int

class OrderResponse(BaseModel):
    purchase_id: int
    purchase_date: datetime
    status: str

class OrderDetails(BaseModel):
    product_id: int
    quantity: int
    subtotal: float
    
############################## USER ##############################
    
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    address: str

class UserResponse(BaseModel):
    customer_id: int
    email: str
    created_at: datetime
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str