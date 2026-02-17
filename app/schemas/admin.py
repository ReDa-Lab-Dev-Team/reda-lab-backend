from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

# Base schema for admin
class AdminBase(BaseModel):
    email: EmailStr
    username: str

# Schema for creating an admin
class AdminCreate(AdminBase):
    password: str

# Schema for admin login
class AdminLogin(BaseModel):
    email: EmailStr
    password: str

# Schema for admin response
class AdminResponse(AdminBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Aliases for backward compatibility
User = AdminResponse
UserCreate = AdminCreate
UserLogin = AdminLogin
UserResponse = AdminResponse

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None