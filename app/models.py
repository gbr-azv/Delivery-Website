from .database import Base
from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Customer(Base):
    __tablename__ = 'customer'

    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15), nullable=False)
    address = Column(String(255), nullable=False)

    purchases = relationship('Purchase', back_populates='customer')

class Product(Base):
    __tablename__ = 'product'

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)

class Purchase(Base):
    __tablename__ = 'purchase'

    purchase_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customer.customer_id'), nullable=False)
    purchase_date = Column(TIMESTAMP, server_default=func.now())
    status = Column(String(20), server_default='Received')

    customer = relationship('Customer', back_populates='purchases')
    items = relationship('PurchaseProduct', back_populates='purchase')
    
    def __repr__(self):
        return (f"Purchase(purchase_id={self.purchase_id}, "
                f"customer_id={self.customer_id}, "
                f"purchase_date={self.purchase_date}, "
                f"status={self.status})")

class PurchaseProduct(Base):
    __tablename__ = 'purchase_product'

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    purchase_id = Column(Integer, ForeignKey('purchase.purchase_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.product_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(DECIMAL(10, 2), nullable=False)

    purchase = relationship('Purchase', back_populates='items')
    product = relationship('Product')