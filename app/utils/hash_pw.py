# this file is for hashing the pw

from passlib.context import CryptContext
# using "bcrypt" algorithm to hash the password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

# to verify the password, we need to compare the hashed password with the plain password
def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
