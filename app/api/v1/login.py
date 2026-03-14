from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.admin import Admin
from app.schemas.admin import Token, AdminLogin
from app.utils import oauth2
    


router = APIRouter(
    prefix="/login",
    tags=["Authentication"],
)
# print("Route: ", router)


@router.post("", response_model=Token)
async def login_admin(admin_credentials: AdminLogin, db: Session = Depends(get_db)):
    
    admin = db.query(Admin).filter(Admin.email == admin_credentials.email).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": "Incorrect email or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not admin.verify_password(admin_credentials.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": "Incorrect email or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = oauth2.create_access_token(
        data={"admin_id": admin.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}



