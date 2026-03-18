from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import os
import shutil
from datetime import datetime
from app.config.database import get_db
from app.schemas.lab_entities import AdvisoryBoardMemberCreate, AdvisoryBoardMemberResponse, AdvisoryBoardMemberUpdate
from app.models.lab_entities import AdvisoryBoardMember
from app.config.config import settings
from app.services.public import UserService

router = APIRouter(prefix="/advisory-board", tags=["Admin - Advisory Board"])
service = UserService() #public service

# ========== READ OPERATIONS ==========

@router.get("", response_model=List[AdvisoryBoardMemberResponse])
async def get_advisory_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_by: str = Query("created_at", pattern="^(name|position|institution|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
     db: Session = Depends(get_db)
     
):
    return await service.get_advisory_members(skip, limit, search, is_active, sort_by, order, db)

@router.get("/{member_id}", response_model=AdvisoryBoardMemberResponse)
async def get_advisory_member(
    member_id: int,
     db: Session = Depends(get_db)
     
):
    db_member = db.query(AdvisoryBoardMember).filter(AdvisoryBoardMember.id == member_id).first()
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Advisory board member with id {member_id} not found"
        )
    return db_member

# ========== CREATE OPERATION ==========

@router.post("", response_model=AdvisoryBoardMemberResponse, status_code=status.HTTP_201_CREATED)
async def create_advisory_member(
    request: Request,
    member: AdvisoryBoardMemberCreate = Depends(AdvisoryBoardMemberCreate.as_form),
    image_url: UploadFile = File(...),
     db: Session = Depends(get_db)
     
):
    try:
        current_admin = request.state.user
        
        # Check if advisory member with same name and position already exists
        existing_member = db.query(AdvisoryBoardMember).filter(
            AdvisoryBoardMember.name == member.name,
            AdvisoryBoardMember.position == member.position
        ).first()
        
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Advisory board member '{member.name}' with position '{member.position}' already exists"
            )
        
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        if image_url.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image type. Allowed types: jpeg, png, jpg, webp"
            )

        # Create upload directory
        path = os.path.join(settings.upload_dir, "advisory_board")
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
                
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = os.path.splitext(image_url.filename)[1]
        filename = f"{member.name.replace(' ', '_')}_{timestamp}{file_ext}"
        file_location = os.path.join(path, filename)
        
        # Save file
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image_url.file, buffer)
            
        # Store relative path in database
        relative_path = os.path.join('advisory_board', filename)
        
        member_data = member.model_dump(exclude_unset=True)
        member_data["image_url"] = relative_path
        
        db_member = AdvisoryBoardMember(**member_data, created_by=current_admin.id)
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member
    except HTTPException:
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Advisory board member already exists or violates unique constraint"
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error occurred"
        )

# ========== UPDATE OPERATION ==========

@router.put("/{member_id}", response_model=AdvisoryBoardMemberResponse)
async def update_advisory_member(
    member_id: int,
    member: AdvisoryBoardMemberUpdate = Depends(AdvisoryBoardMemberUpdate.as_form),
    image_url: Optional[UploadFile] = File(None),
     db: Session = Depends(get_db)
     
):
    db_member = db.query(AdvisoryBoardMember).filter(AdvisoryBoardMember.id == member_id).first()
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Advisory board member with id {member_id} not found"
        )
    
    try:
        update_data = member.model_dump(exclude_unset=True, exclude_none=True)
        
        # Update only provided fields
        for key, value in update_data.items():
            setattr(db_member, key, value)
        
        # Handle photo upload
        if image_url:
            # Validate file type
            allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
            if image_url.content_type not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image type. Allowed types: jpeg, png, jpg, webp"
                )
            
            try:
                # Delete old photo if exists
                if db_member.image_url:
                    old_photo_path = os.path.join(settings.upload_dir, db_member.image_url)
                    if os.path.exists(old_photo_path):
                        try:
                            os.remove(old_photo_path)
                        except Exception as e:
                            print(f"Warning: Could not delete old photo: {e}")
                
                # Create upload directory
                path = os.path.join(settings.upload_dir, 'advisory_board')
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                
                # Create unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_ext = os.path.splitext(image_url.filename)[1]
                filename = f"{db_member.name.replace(' ', '_')}_{timestamp}{file_ext}"
                file_location = os.path.join(path, filename)
                
                # Save file
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(image_url.file, buffer)
                
                # Store relative path
                relative_path = os.path.join('advisory_board', filename)
                db_member.image_url = relative_path
                
            except Exception as e:
                # Cleanup on error
                if 'file_location' in locals() and os.path.exists(file_location):
                    os.remove(file_location)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload photo: {str(e)}"
                )
        
        db.commit()
        db.refresh(db_member)
        return db_member
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Update violates unique constraint"
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error occurred"
        )

# ========== DELETE OPERATION ==========

@router.delete("/{member_id}", status_code=status.HTTP_200_OK)
async def delete_advisory_member(
    member_id: int,
     db: Session = Depends(get_db)
     
):
    db_member = db.query(AdvisoryBoardMember).filter(AdvisoryBoardMember.id == member_id).first()
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Advisory board member with id {member_id} not found"
        )
    
    try:
        # Delete associated photo if it exists
        if db_member.image_url:
            photo_path = os.path.join(settings.upload_dir, db_member.image_url)
            if os.path.exists(photo_path):
                try:
                    os.remove(photo_path)
                except Exception as e:
                    print(f"Warning: Could not delete photo file: {e}")

        db.delete(db_member)
        db.commit()
        return {"message": "Advisory board member deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete advisory board member"
        )