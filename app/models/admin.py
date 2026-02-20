from sqlalchemy import Column, Integer, String, Boolean, DateTime, TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import func

from app.config.database import Base
from pwdlib import PasswordHash


class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String(20), nullable=True, default="admin")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    _pwd_hash = PasswordHash.recommended()


    """
        we just include this 2 functions from utils , so that we can easily call it from 
        the model itself, and we don't need to import the utils every time we want to hash 
        or verify the password, the operation still the same
    """ 
    def set_password(self, password: str):
        self.hashed_password = self._pwd_hash.hash(password)

    def verify_password(self, password: str) -> bool:
        return self._pwd_hash.verify(password, self.hashed_password)
