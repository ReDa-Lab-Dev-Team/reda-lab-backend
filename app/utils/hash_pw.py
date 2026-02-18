# this file is for hashing the pw

from pwdlib import PasswordHash

# using Argon2 algorithm to hash the password
pwd_hash = PasswordHash.recommended()

def hash_pw(password: str):
    return pwd_hash.hash(password)

# to verify the password, we need to compare the hashed password with the plain password
def verify_password(plain_password: str, hashed_password: str):
    return pwd_hash.verify(plain_password, hashed_password)