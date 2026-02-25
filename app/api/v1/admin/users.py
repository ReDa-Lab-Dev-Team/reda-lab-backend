from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Response
from app.schemas.admin import AdminCreate, AdminResponse, AdminUpdate
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.oauth2 import get_current_user
from app.models.admin import Admin
import os
import shutil
from app.config.config import settings
from datetime import datetime

router = APIRouter(prefix="/user", tags=["Admin - Users"])

# PUBLIC ROUTE - No authentication required
@router.post("/register", response_model=AdminResponse)
async def create(admin: AdminCreate, db: Session = Depends(get_db)):
    db_admin = db.query(Admin).filter(
        (Admin.email == admin.email) | (Admin.username == admin.username)
    ).first()
    
    if db_admin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail={"msg": "Email or username already registered"}
        )

    new_admin = Admin(
        email=admin.email,
        username=admin.username,
    )
    new_admin.set_password(admin.password)
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

# PROTECTED ROUTES - Authentication required
@router.get("/all_admins", response_model=list[AdminResponse])
async def read_all_admins(
    current_admin: AdminResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    admins = db.query(Admin).all()
    return admins

@router.get("/me", response_model=AdminResponse)
async def read_admin_me(current_admin: AdminResponse = Depends(get_current_user)):
    return current_admin

@router.patch("/update/{admin_id}", response_model=AdminResponse)
async def update_admin(
    admin_id: int,
    admin_update: AdminUpdate,
    current_admin: AdminResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
    
    # Update only provided fields
    update_data = admin_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "password":
            admin.set_password(value)
        else:
            setattr(admin, field, value)
    
    db.commit()
    db.refresh(admin)
    return admin

@router.post("/{admin_id}/avatar")
async def upload_avatar(
    admin_id: int,
    file: UploadFile = File(...),
    current_admin: AdminResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload avatar (creates new or replaces existing)"""
    try:
        # Allow superadmin to upload avatar for any account OR users to upload their own
        if current_admin.role != "superadmin" and current_admin.id != admin_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"msg": "Not authorized to update this account"}
            )
        
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"msg": "Only image files are allowed (JPEG, PNG, WebP)"}
            )
        
        # Check if admin exists BEFORE uploading
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"msg": "Admin not found"}
            )
        
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
        
        # Create unique filename with safe extension
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"admin_{admin_id}_{timestamp}{file_ext}"
        file_location = os.path.join(path, filename)
        
        # Save file
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Store relative path instead of absolute
        relative_path = os.path.join('user', filename)
        admin.avatar = relative_path
        
        db.commit()
        db.refresh(admin)
        
        return {
            "avatar_url": f"/upload/{relative_path}",
            "msg": "Avatar uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Cleanup on error
        if 'file_location' in locals() and os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"msg": f"Failed to upload avatar: {str(e)}"}
        )

@router.delete("/delete/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin(
    admin_id: int,
    current_admin: AdminResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only allow superadmin to delete accounts
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