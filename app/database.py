from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Sets the connection URL to the PostgreSQL database
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:e3rxapap@postgres:5432/FastAPI'

# Creates an instance of SQLAlchemy create_engine, which represents the database connection
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a sessionmaker class
# This class is used to create instances of database sessions
# Autocommit=False: transactions are not automatically committed after each database operation
# Autoflush=False: the session is not automatically flushed before each query (better control over syncs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creates a base class for declarative models (starting point for defining SQLAlchemy models)
Base = declarative_base()

# This function is used as a generator to obtain a database session
# Using yield allows the function to be used as a generator 
# and ensures that the session is closed (db.close()) after use
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()