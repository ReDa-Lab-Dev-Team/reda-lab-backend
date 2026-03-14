from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, desc, asc
import os
import shutil
from app.config.database import get_db
from app.schemas.lab_entities import ResearchClubCreate, ResearchClubResponse, ResearchClubUpdate
from app.models.lab_entities import ResearchClub
from app.utils.helper_functions import slugify
from app.config.config import settings
from datetime import datetime
from app.services.public import UserService

router = APIRouter(prefix="/research-clubs", tags=["Admin - Research Clubs"])
service = UserService()

# ========== READ OPERATIONS ==========

@router.get("", response_model=List[ResearchClubResponse])
async def get_all_research_clubs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_by: str = Query("created_at", pattern="^(name|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
     db: Session = Depends(get_db)
     
):
    return await service.get_research_clubs(skip, limit, search, is_active, sort_by, order, db)

@router.get("/{club_id}", response_model=ResearchClubResponse)
async def get_research_club(
    club_id: int,
     db: Session = Depends(get_db)
     
):
    db_club = db.query(ResearchClub).filter(ResearchClub.id == club_id).first()
    if not db_club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research club with id {club_id} not found"
        )
    return db_club

# ========== CREATE OPERATION ==========

@router.post("", response_model=ResearchClubResponse, status_code=status.HTTP_201_CREATED)
async def create_research_club(
    request: Request,
    club: ResearchClubCreate = Depends(ResearchClubCreate.as_form),
    image_url: UploadFile = File(...),
     db: Session = Depends(get_db)
     
):
    try:
        current_admin = request.state.user
        
        # convert pydantic model to dict and exclude unset fields
        new_club_data = club.model_dump(exclude_unset=True)
        new_club_data["slug"] = slugify(club.name)
        
        existing_club = db.query(ResearchClub).filter(
            ResearchClub.slug == new_club_data["slug"]
        ).first()
        if existing_club:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Research club with the same name already exists"
            )
        
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        if image_url.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image type. Allowed types: jpeg, png, jpg, webp"
            )

        # Create upload directory
        path = os.path.join(settings.upload_dir, "research_clubs")
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
                
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = os.path.splitext(image_url.filename)[1]
        filename = f"{new_club_data['slug']}_{timestamp}{file_ext}"
        file_location = os.path.join(path, filename)
        
        # Save file
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image_url.file, buffer)
            
        # Store relative path in database
        relative_path = os.path.join('research_clubs', filename)
        new_club_data["image_url"] = relative_path
        
        db_club = ResearchClub(**new_club_data, created_by=current_admin.id)
        db.add(db_club)
        db.commit()
        db.refresh(db_club)
        return db_club
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Research club already exists or violates unique constraint"
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error occurred"
        )

# ========== UPDATE OPERATION ==========

@router.put("/{club_id}", response_model=ResearchClubResponse)
async def update_research_club(
    club_id: int,
    club: ResearchClubUpdate = Depends(ResearchClubUpdate.as_form),
    image_url: Optional[UploadFile] = File(None),
     db: Session = Depends(get_db)
     
):
    db_club = db.query(ResearchClub).filter(ResearchClub.id == club_id).first()
    if not db_club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Research club with id {club_id} not found"
        )
  
    try:
        update_data = club.model_dump(exclude_unset=True, exclude_none=True)
        
        # Only update slug if name is provided and not None
        if "name" in update_data and update_data["name"]:
            new_slug = slugify(update_data["name"])
            
            # Check slug uniqueness (if changed)
            if new_slug != db_club.slug:
                existing_club = db.query(ResearchClub).filter(
                    ResearchClub.slug == new_slug,
                    ResearchClub.id != club_id
                ).first()
                
                if existing_club:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Research Club with the same name already exists"
                    )
                update_data["slug"] = new_slug
        
        # Update only provided fields
        for key, value in update_data.items():
            setattr(db_club, key, value)
        
        # Handle image_url upload
        if image_url:
            # Validate file type
            allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
            if image_url.content_type not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image type. Allowed types: jpeg, png, jpg, webp"
                )
            
            try:
                # Delete old image_url if exists
                if db_club.image_url:
                    old_image_url_path = os.path.join(settings.upload_dir, db_club.image_url)
                    if os.path.exists(old_image_url_path):
                        try:
                            os.remove(old_image_url_path)
                        except Exception as e:
                            print(f"Warning: Could not delete old image_url: {e}")
                
                # Create upload directory
                path = os.path.join(settings.upload_dir, 'research_clubs')
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                
                # Create unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_ext = os.path.splitext(image_url.filename)[1]
                filename = f"{db_club.slug}_{timestamp}{file_ext}"
                file_location = os.path.join(path, filename)
                
                # Save file
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(image_url.file, buffer)
                
                # Store relative path
                relative_path = os.path.join('research_clubs', filename)
                db_club.image_url = relative_path
                
            except Exception as e:
                # Cleanup on error
                if 'file_location' in locals() and os.path.exists(file_location):
                    os.remove(file_location)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload image_url: {str(e)}"
                )
       
        db.commit()
        db.refresh(db_club)
        return db_club
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

@router.delete("/{club_id}", status_code=status.HTTP_200_OK)
async def delete_research_club(
    club_id: int,
     db: Session = Depends(get_db)
     
):
    db_club = db.query(ResearchClub).filter(ResearchClub.id == club_id).first()
    if not db_club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Research club with id {club_id} not found"
        )
    
    try:
        # Delete associated image if it exists
        if db_club.image_url:
            image_path = os.path.join(settings.upload_dir, db_club.image_url)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Warning: Could not delete image file: {e}")

        db.delete(db_club)
        db.commit()
        return {"message": "Research club deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete research club"
        )