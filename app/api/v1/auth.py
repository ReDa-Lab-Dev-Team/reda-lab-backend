from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.config.database import get_db
from app.models.user import User as ModelUser
from app.schemas.user import UserCreate, User as SchemaUser, Token, UserLogin
from app.utils.auth import (
    authenticate_user, create_access_token, get_password_hash, get_current_active_user
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register", response_model=SchemaUser)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(ModelUser).filter(
        (ModelUser.email == user.email) | (ModelUser.username == user.username)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=400, detail="Email or username already registered")

    hashed_password = get_password_hash(user.password)
    db_user = ModelUser(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=SchemaUser)
async def read_users_me(current_user: SchemaUser = Depends(get_current_active_user)):
    return current_user