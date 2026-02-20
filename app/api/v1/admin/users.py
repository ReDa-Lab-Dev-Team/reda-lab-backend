from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile, Response
from app.schemas.admin import AdminCreate, AdminResponse
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.oauth2 import get_current_user
from app.utils import oauth2
from app.models.admin import Admin
import os
import shutil
from app.config.config import settings
from datetime import datetime

router = APIRouter(prefix="/user", tags=["Admin - Users"])

# implement Crud

@router.post("", response_model=AdminResponse)
async def create(admin: AdminCreate, db: Session = Depends(get_db)):
    db_admin = db.query(Admin).filter(
        (Admin.email == admin.email) | (Admin.username == admin.username)
    ).first()
    
    if db_admin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail={"msg": "Email or username already registered"})

    new_admin = Admin(
        email=admin.email,
        username=admin.username,
    )
    new_admin.set_password(admin.password)
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

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
    admin.set_password(admin_update.password)
    
    db.commit()
    db.refresh(admin)
    return admin

@router.post("/{admin_id}/avatar")
async def upload_avatar(
    admin_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):    
    try:
        # handle file upload and update user's avatar URL in the database
        path = os.path.join(settings.upload_dir, 'user')
        if not os.path.exists(path):
            os.makedirs(path)
            
        # create unique name file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_location = os.path.join(path, filename)
        
        # Save the file
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # update user's avatar URL in the database
        db_user = db.query(Admin).filter(Admin.id == admin_id).first()
        if not db_user:
            # Delete the uploaded file if user not found
            if os.path.exists(file_location):
                os.remove(file_location)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"msg": f"Admin with id {admin_id} not found"}
            )
        
        db_user.avatar = file_location
        db.commit()
        db.refresh(db_user)
        return {"avatar_url": file_location, "msg": "Avatar uploaded successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up file if it was created
        if 'file_location' in locals() and os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"msg": f"Failed to upload avatar: {str(e)}"}
        )

@router.put("/{admin_id}/avatar")
async def update_avatar(
    admin_id: int,
    current_admin: AdminResponse = Depends(get_current_user),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Only allow admins to update their own account or check for admin privileges
        if current_admin.id != admin_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"msg": "Not authorized to update this account"}
            )
        
        # Check if admin exists
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"msg": "Admin not found"}
            )
        
        # Store old avatar path for rollback
        old_avatar = admin.avatar
        
        # Delete old avatar file if exists
        if admin.avatar and os.path.exists(admin.avatar):
            try:
                os.remove(admin.avatar)
            except Exception as e:
                print({"msg": f"Error deleting old avatar: {e}"})
        
        # Create upload directory if it doesn't exist
        path = os.path.join(settings.upload_dir, 'user')
        if not os.path.exists(path):
            os.makedirs(path)
        
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_location = os.path.join(path, filename)
        
        # Save the file
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update admin's avatar in database
        admin.avatar = file_location
        db.commit()
        db.refresh(admin)
        
        return {"avatar_url": file_location, "msg": "Avatar updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up new file if it was created
        if 'file_location' in locals() and os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"msg": f"Failed to update avatar: {str(e)}"}
        )


@router.delete("/delete/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin(
    admin_id: int,
    current_admin: AdminResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only allow super admin to delete accounts
    if current_admin.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"msg": "Only super admin can delete accounts"}
        )
    
    # Prevent super admin from deleting themselves
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
    if admin.avatar and os.path.exists(admin.avatar):
        try:
            os.remove(admin.avatar)
        except Exception as e:
            print({"msg": f"Error deleting avatar: {e}"})
    
    db.delete(admin)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
