from uuid import uuid4
#
from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
#
from .database import Base

class Customer(Base):
    #  "__tablename__": Special attribute in SQLAlchemy that specifies the name 
    # of the table in the database associated with this class
    __tablename__ = 'customer'

    # These definitions provide the characteristics of the fields in the table associated 
    # with the class in the context of SQLAlchemy
    # Each field is an instance of the SQLAlchemy Column class
    customer_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String(15), nullable=False)
    address = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Creates a relationship between the tables associated with the Customer and Purchase classes
    # Establishing a two-way relationship
    purchases = relationship('Purchase', back_populates='customer')

class Product(Base):

    __tablename__ = 'product'

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)

class Purchase(Base):
    __tablename__ = 'purchase'

    purchase_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customer.customer_id', ondelete="CASCADE"), nullable=False)
    purchase_date = Column(TIMESTAMP, server_default=func.now())
    status = Column(String(20), server_default='Received')

    # Creates a relationship between the Purchase class and the Customer class
    # Establishing a two-way relationship
    customer = relationship('Customer', back_populates='purchases')
    
    # Creates a relationship between the Purchase class and the PurchaseProduct class
    # Establishing a two-way relationship
    items = relationship('PurchaseProduct', back_populates='purchase')

class PurchaseProduct(Base):
    __tablename__ = 'purchase_product'

    item_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    purchase_id = Column(UUID(as_uuid=True), ForeignKey('purchase.purchase_id', ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey('product.product_id', ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(DECIMAL(10, 2), nullable=False)

    # Creates a relationship between the PurchaseProduct class and the Purchase class
    # Establishing a two-way relationship
    purchase = relationship('Purchase', back_populates='items')
    
    # Creates a relationship between the PurchaseProduct class and the Product class
    # Establishing a ONE-WAY relationship
    product = relationship('Product')