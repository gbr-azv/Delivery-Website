from datetime import datetime
from pydantic import BaseModel

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
    
class AllOrderResponse(OrderResponse):
    pass

class OrderDetails(BaseModel):
    product_id: int
    quantity: int
    subtotal: float