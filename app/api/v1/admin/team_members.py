from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, desc, asc, func
import os
import shutil
from datetime import datetime

from app.config.database import get_db
from app.models.admin import Admin
from app.schemas.lab_entities import TeamMemberCreate, TeamMemberResponse, TeamMemberUpdate
from app.models.lab_entities import TeamMember
from app.config.config import settings

router = APIRouter(prefix="/team-members", tags=["Admin - Team Members"])

# ========== READ OPERATIONS ==========

@router.get("/count", response_model=Dict[str, int])
async def count_team_members(
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
     db: Session = Depends(get_db)
     
):

    try:
        query = db.query(func.count(TeamMember.id))
        
        if is_active is not None:
            query = query.filter(TeamMember.is_active == is_active)
        
        if search:
            query = query.filter(
                or_(
                    TeamMember.name.ilike(f"%{search}%"),
                    TeamMember.position.ilike(f"%{search}%"),
                    TeamMember.bio.ilike(f"%{search}%")
                )
            )
        
        total = query.scalar()
        return {"total": total}
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to count team members"
        )

@router.get("", response_model=List[TeamMemberResponse])
async def get_all_team_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_by: str = Query("created_at", pattern="^(name|position|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
     db: Session = Depends(get_db)
      
):
    try:
        query = db.query(TeamMember)

        if search:
            query = query.filter(
                or_(
                    TeamMember.name.ilike(f"%{search}%"),
                    TeamMember.position.ilike(f"%{search}%"),
                    TeamMember.bio.ilike(f"%{search}%")
                )
            )

        if is_active is not None:
            query = query.filter(TeamMember.is_active == is_active)

        order_func = desc if order == "desc" else asc
        query = query.order_by(order_func(getattr(TeamMember, sort_by)))
        
        # Apply pagination
        members = query.offset(skip).limit(limit).all()
        return members
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve team members"
        )

@router.get("/{member_id}", response_model=TeamMemberResponse)
async def get_team_member_id(
    member_id: int,
     db: Session = Depends(get_db)
     
):

    db_member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team member with id {member_id} not found"
        )
    return db_member

# ========== CREATE OPERATION ==========

@router.post("", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
async def create_team_member(
    request: Request,
    member: TeamMemberCreate = Depends(TeamMemberCreate.as_form),
    image_url: Optional[UploadFile] = File(None),
     db: Session = Depends(get_db)
     
):

    try:
        current_admin = request.state.user
        member_data = member.model_dump(exclude_unset=True)
        
        if image_url:
            # Validate file type
            allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
            if image_url.content_type not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image type. Allowed types: jpeg, png, jpg, webp"
                )

            # Create upload directory
            path = os.path.join(settings.upload_dir, "team_members")
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
            relative_path = os.path.join('team_members', filename)
            member_data["image_url"] = relative_path
        
        db_member = TeamMember(**member_data, created_by=current_admin.id)
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Team member already exists or violates unique constraint"
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error occurred"
        )

# ========== UPDATE OPERATION ==========

@router.put("/{member_id}", response_model=TeamMemberResponse)
async def update_team_member(
    member_id: int,
    member: TeamMemberUpdate = Depends(TeamMemberUpdate.as_form),
    image_url: Optional[UploadFile] = File(None),
     db: Session = Depends(get_db)
     
):
    """Update an existing team member (Admin only)"""
    db_member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Team member with id {member_id} not found"
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
                path = os.path.join(settings.upload_dir, 'team_members')
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
                relative_path = os.path.join('team_members', filename)
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

@router.delete("/delete/{member_id}", status_code=status.HTTP_200_OK)
async def delete_team_member(
    member_id: int,
     db: Session = Depends(get_db)
     
):
    """Delete a team member (Admin only)"""
    db_member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Team member with id {member_id} not found"
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
        return {"detail": f"Team member with id {member_id} deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete team member"
        )