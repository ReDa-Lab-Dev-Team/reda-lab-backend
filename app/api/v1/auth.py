from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.admin import Admin
from app.schemas.admin import AdminCreate, AdminResponse, Token, AdminLogin
from app.utils import oauth2
from app.utils.hash_pw import hash_pw, verify_password
from app.utils.oauth2 import get_current_user

    


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
            status_code=status.HTTP_409_CONFLICT, detail={"msg": "Email or username already registered"})

    hashed_password = hash_pw(admin.password)
    new_admin = Admin(
        email=admin.email,
        username=admin.username,
        hashed_password=hashed_password
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

@router.post("/login", response_model=Token)
async def login_admin(admin_credentials: AdminLogin = Depends(), db: Session = Depends(get_db)):
    
    admin = db.query(Admin).filter(Admin.email == admin_credentials.email).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": "Incorrect email or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not verify_password(admin_credentials.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": "Incorrect email or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = oauth2.create_access_token(
        data={"admin_id": admin.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/all_admins", response_model=list[AdminResponse])
async def read_all_admins(current_admin: AdminResponse = Depends(get_current_user),db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    if current_admin.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail={"msg": "Not authorized to perform requested action!"})
    admins = db.query(Admin).all()
    return admins

@router.get("/me", response_model=AdminResponse)
async def read_admin_me(current_admin: AdminResponse = Depends(get_current_user)):
    return current_admin


@router.put("/update/{admin_id}", response_model=AdminResponse)
async def update_admin(
    admin_id: int,
    admin_update: AdminCreate,
    current_admin: AdminResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only allow admins to update their own account or check for admin privileges
    if current_admin.id != admin_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": "Not authorized to update this account"}
        )
    
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "Admin not found"}
        )
    
    # Check if email/username already exists for another admin
    existing_admin = db.query(Admin).filter(
        Admin.id != admin_id,
        (Admin.email == admin_update.email) | (Admin.username == admin_update.username)
    ).first()
    
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"msg": "Email or username already in use"}
        )
    
    admin.email = admin_update.email
    admin.username = admin_update.username
    admin.hashed_password = hash_pw(admin_update.password)
    
    db.commit()
    db.refresh(admin)
    return admin

@router.delete("/delete/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin(
    admin_id: int,
    current_admin: AdminResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only allow admins to delete their own account
    if current_admin.id != admin_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this account"
        )
    
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    
    db.delete(admin)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)