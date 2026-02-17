from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.config.database import get_db
from app.models.admin import Admin
from app.schemas.admin import AdminCreate, AdminResponse, Token, AdminLogin
from app.utils.oauth2 import (
    authenticate_user, create_access_token, get_password_hash, get_current_active_user
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register", response_model=AdminResponse)
async def register_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    db_admin = db.query(Admin).filter(
        (Admin.email == admin.email) | (Admin.username == admin.username)
    ).first()
    if db_admin:
        raise HTTPException(
            status_code=400, detail="Email or username already registered")

    hashed_password = get_password_hash(admin.password)
    db_admin = Admin(
        email=admin.email,
        username=admin.username,
        hashed_password=hashed_password
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

@router.post("/login", response_model=Token)
async def login_admin(admin_credentials: AdminLogin, db: Session = Depends(get_db)):
    admin = authenticate_user(db, admin_credentials.email, admin_credentials.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": admin.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=AdminResponse)
async def read_admin_me(current_admin: AdminResponse = Depends(get_current_active_user)):
    return current_admin