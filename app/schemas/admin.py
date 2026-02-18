from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from typing import Optional
from datetime import datetime
from fastapi import Form

# Base schema for admin
class AdminBase(BaseModel):
    email: EmailStr
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        if not v.endswith('@gmail.com'):
            raise ValueError('Email must be from @gmail.com domain')
        return v
    username: str

# Schema for creating an admin
class AdminCreate(AdminBase):
    password: str

# Schema for admin login
class AdminLogin:
    def __init__(
        self,
        email: EmailStr = Form(...),
        password: str = Form(...)
    ):
        self.email = email
        self.password = password

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
    id: Optional[int] = None
    