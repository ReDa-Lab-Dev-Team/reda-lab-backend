from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Response,Request
from app.schemas.admin import AdminCreate, AdminResponse, AdminUpdate
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.admin import Admin
import os
import shutil
from app.config.config import settings
from datetime import datetime
from typing import Optional
from app.services.public import UserService

router = APIRouter(prefix="/user", tags=["Admin - Users"])

# service = UserService()
@router.post("/register",response_model=AdminResponse)
async def create(admin: AdminCreate = Depends(AdminCreate.as_form),
                 avatar: UploadFile = File(...),
                 db: Session = Depends(get_db)):
    
    db_admin = db.query(Admin).filter(
        (Admin.email == admin.email) | (Admin.username == admin.username)
    ).first()
    
    if db_admin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail={"msg": "Email or username already registered"}
        )
        
    # Handle avatar upload
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if avatar.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Only image files are allowed (JPEG, PNG, JPG, WebP)"}
        )
        
    if avatar:
        # Create upload directory
        path = os.path.join(settings.upload_dir, 'user')
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        
        # Create unique filename with safe extension
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = os.path.splitext(avatar.filename)[1]
        filename = f"admin_{timestamp}{file_ext}"
        file_location = os.path.join(path, filename)
        
        # Save file
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(avatar.file, buffer)
    else:
        file_location = None
        
    new_admin = Admin(
        email=admin.email,
        username=admin.username,
        avatar=file_location
    )
    
    new_admin.set_password(admin.password)
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin


@router.get("", response_model=list[AdminResponse])
async def read_all_admins(
    db: Session = Depends(get_db)
):
    admins = db.query(Admin).all()
    
    return admins
    # return service.get_users(db)


@router.get("/me", response_model=AdminResponse)
async def read_admin_me(request: Request):
    user = request.state.user
    return user

@router.patch("/update/{admin_id}", response_model=AdminResponse)
async def update_admin(
    request: Request,
    admin_id: int,
    admin_update: AdminUpdate = Depends(AdminUpdate.as_form),
    avatar: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    current_admin = request.state.user
    # Allow superadmin to update any account OR users to update their own account
    if current_admin.role != "superadmin" and current_admin.id != admin_id:
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
    
    # Check if email/username already exists for another admin (only if being updated)
    if admin_update.email or admin_update.username:
        filters = []
        if admin_update.email:
            filters.append(Admin.email == admin_update.email)
        if admin_update.username:
            filters.append(Admin.username == admin_update.username)
            
        existing_admin = db.query(Admin).filter(
            Admin.id != admin_id,
            *filters
        ).first()
        
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"msg": "Email or username already in use"}
            )
    
    # Update only provided fields from schema
    update_data = admin_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if value is not None:  # Skip None values
            if field == "password":
                admin.set_password(value)
            else:
                setattr(admin, field, value)
    
    # Handle avatar upload
    if avatar:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        if avatar.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"msg": "Only image files are allowed (JPEG, PNG, WebP)"}
            )
        
        try:
            # Delete old avatar if exists
            if admin.avatar:
                old_avatar_path = os.path.join(settings.upload_dir, admin.avatar)
                if os.path.exists(old_avatar_path):
                    try:
                        os.remove(old_avatar_path)
                    except Exception as e:
                        print(f"Warning: Could not delete old avatar: {e}")
            
            # Create upload directory
            path = os.path.join(settings.upload_dir, 'user')
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            
            # Create unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_ext = os.path.splitext(avatar.filename)[1]
            filename = f"admin_{admin_id}_{timestamp}{file_ext}"
            file_location = os.path.join(path, filename)
            
            # Save file
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(avatar.file, buffer)
            
            # Store relative path
            relative_path = os.path.join('user', filename)
            admin.avatar = relative_path
            
        except Exception as e:
            # Cleanup on error
            if 'file_location' in locals() and os.path.exists(file_location):
                os.remove(file_location)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"msg": f"Failed to upload avatar: {str(e)}"}
            )
    
    db.commit()
    db.refresh(admin)
    return admin

@router.delete("/delete/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin(
    request: Request,
    admin_id: int,
    db: Session = Depends(get_db)
):
    
    # Only allow superadmin to delete accounts
    current_admin = request.state.user
    if current_admin.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": "Only super admin can delete accounts"}
        )
    
    # Prevent superadmin from deleting themselves
    if current_admin.id == admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"msg": "Cannot delete your own account"}
        )
    
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "Admin not found"}
        )
    
    # Delete avatar file if exists
    if admin.avatar:
        avatar_path = os.path.join(settings.upload_dir, admin.avatar)
        if os.path.exists(avatar_path):
            try:
                os.remove(avatar_path)
            except Exception as e:
                print(f"Error deleting avatar: {e}")
    
    db.delete(admin)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)