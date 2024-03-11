from passlib.context import CryptContext

# This file uses the "passlib" library to handle password hashing securely

# Creates an instance of the encryption context (CryptContext) using the "bcrypt" hash scheme
# Deprecated="auto": indicates that the "bcrypt" scheme should be used, 
# but the library can automatically switch to a more secure scheme in the future if necessary
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Takes a password as input and returns the password hash using the scheme configured in pwd_context
def hash(password: str):
    
    # The "CryptContext" hash method hashes the password
    return pwd_context.hash(password)

# Checks whether an unencrypted password (plain_password) matches the stored password hash (hashed_password)
def verify(plain_password, hashed_password):
    
    # Uses the "CryptContext" verify method to perform the verification
    return pwd_context.verify(plain_password, hashed_password)