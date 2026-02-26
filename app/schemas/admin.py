from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator, ValidationError
from typing import Optional
from datetime import datetime
from fastapi import Depends, Form, HTTPException, status

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
# class AdminCreate(AdminBase):
#     password: str

class AdminCreate(AdminBase):
    password: str

    @classmethod
    def as_form(
        cls,
        email: EmailStr = Form(...),
        username: str = Form(...),
        password: str = Form(...)
    ):
        try:
            return cls(
                email=email,
                username=username,
                password=password
            )
        except ValidationError as e:
            # Extract the error message
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', 'Validation error')
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"msg": error_msg}
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"msg": "Invalid input data"}
            )
    
class AdminUploadAvatar(BaseModel):
    avatar: str

# Schema for admin login
# class AdminLogin:
#     def __init__(
#         self,
#         email: EmailStr = Form(...),
#         password: str = Form(...)
#     ):
#         self.email = email
#         self.password = password

class AdminLogin(BaseModel):
    email: EmailStr
    password: str
    
# Schema for admin response
class AdminResponse(AdminBase):
    id: int
    is_active: bool
    role: str
    created_at: datetime
    avatar: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
    
class AdminUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        if v is not None and not v.endswith('@gmail.com'):
            raise ValueError('Email must be from @gmail.com domain')
        return v

    @classmethod
    def as_form(
        cls,
        email: Optional[EmailStr] = Form(None),
        username: Optional[str] = Form(None),
        password: Optional[str] = Form(None)
    ):
        try:
            return cls(email=email, username=username, password=password)
        except ValidationError as e:
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', 'Validation error')
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"msg": error_msg}
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"msg": "Invalid input data"}
            )


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None
    