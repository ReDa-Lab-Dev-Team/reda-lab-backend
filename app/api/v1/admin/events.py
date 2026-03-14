from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, desc, asc
import os
import shutil
from datetime import datetime
from app.config.database import get_db
from app.schemas.lab_entities import EventCreate, EventResponse, EventUpdate
from app.models.lab_entities import Event, EventType
from app.config.config import settings
from app.utils.helper_functions import slugify

router = APIRouter(prefix="/events", tags=["Admin - Events"])

# ========== READ OPERATIONS ==========

@router.get("", response_model=List[EventResponse])
async def get_all_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    event_type: Optional[EventType] = None,
    is_active: Optional[bool] = None,
    sort_by: str = Query("created_at", pattern="^(title|start_datetime|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
     db: Session = Depends(get_db)
     
):
    try:
        query = db.query(Event)

        if search:
            query = query.filter(
                or_(
                    Event.title.ilike(f"%{search}%"),
                    Event.description.ilike(f"%{search}%"),
                    Event.location.ilike(f"%{search}%")
                )
            )

        if event_type:
            query = query.filter(Event.event_type == event_type)

        if is_active is not None:
            query = query.filter(Event.is_active == is_active)

        order_func = desc if order == "desc" else asc
        query = query.order_by(order_func(getattr(Event, sort_by)))
        
        # Apply pagination
        events = query.offset(skip).limit(limit).all()
        return events
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve events"
        )

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
     db: Session = Depends(get_db)
     
):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    return db_event

# ========== CREATE OPERATION ==========

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    request: Request,
    event: EventCreate = Depends(EventCreate.as_form),
    image_url: UploadFile = File(...),
     db: Session = Depends(get_db)
     
):
    try:
        current_admin = request.state.user
        
        # Convert Pydantic model to dictionary
        event_data = event.model_dump(exclude_unset=True)
        event_data["slug"] = slugify(event.title)
        
        existing_event = db.query(Event).filter(
            Event.slug==event_data["slug"]
        ).first()
        if existing_event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event with this slug already exists"
            )
        
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        if image_url.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image type. Allowed types: jpeg, png, jpg, webp"
            )

        # Create upload directory
        path = os.path.join(settings.upload_dir, "events")
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
                
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = os.path.splitext(image_url.filename)[1]
        filename = f"{event_data['slug']}_{timestamp}{file_ext}"
        file_location = os.path.join(path, filename)
        
        # Save file
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(image_url.file, buffer)
            
        # Store relative path in database
        relative_path = os.path.join('events', filename)
        event_data["image_url"] = relative_path
        
        db_event = Event(**event_data, created_by=current_admin.id)
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Event already exists or violates unique constraint"
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error occurred"
        )

# ========== UPDATE OPERATION ==========

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event: EventUpdate = Depends(EventUpdate.as_form),
    image_url: Optional[UploadFile] = File(None),
     db: Session = Depends(get_db)
     
):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Event with id {event_id} not found"
        )
    
    try:
        update_data = event.model_dump(exclude_unset=True, exclude_none=True)
        
        # Only update slug if title is provided and not None
        if "title" in update_data and update_data["title"]:
            new_slug = slugify(update_data["title"])
            
            # Check slug uniqueness (if changed)
            if new_slug != db_event.slug:
                existing_event = db.query(Event).filter(
                    Event.slug == new_slug,
                    Event.id != event_id
                ).first()
                
                if existing_event:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Event with the same title already exists"
                    )
                update_data["slug"] = new_slug
        
        # Update only provided fields
        for key, value in update_data.items():
            setattr(db_event, key, value)
        
        # Handle image upload
        if image_url:
            # Validate file type
            allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
            if image_url.content_type not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image type. Allowed types: jpeg, png, jpg, webp"
                )
            
            try:
                # Delete old image if exists
                if db_event.image_url:
                    old_image_path = os.path.join(settings.upload_dir, db_event.image_url)
                    if os.path.exists(old_image_path):
                        try:
                            os.remove(old_image_path)
                        except Exception as e:
                            print(f"Warning: Could not delete old image: {e}")
                
                # Create upload directory
                path = os.path.join(settings.upload_dir, 'events')
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                
                # Create unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_ext = os.path.splitext(image_url.filename)[1]
                filename = f"{db_event.slug}_{timestamp}{file_ext}"
                file_location = os.path.join(path, filename)
                
                # Save file
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(image_url.file, buffer)
                
                # Store relative path
                relative_path = os.path.join('events', filename)
                db_event.image_url = relative_path
                
            except Exception as e:
                # Cleanup on error
                if 'file_location' in locals() and os.path.exists(file_location):
                    os.remove(file_location)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload image: {str(e)}"
                )
        
        db.commit()
        db.refresh(db_event)
        return db_event
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

@router.delete("/{event_id}", status_code=status.HTTP_200_OK)
async def delete_event(
    event_id: int,
     db: Session = Depends(get_db)
     
) :
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Event with id {event_id} not found"
        )
    
    try:
        # Delete associated image if it exists
        if db_event.image_url:
            image_path = os.path.join(settings.upload_dir, db_event.image_url)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Warning: Could not delete image file: {e}")

        db.delete(db_event)
        db.commit()
        return {"message": "Event deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete event"
        )

# # ========== FILE UPLOAD ==========

# @router.post("/{event_id}/upload-image")
# async def upload_event_image(
#     event_id: int,
#     file: UploadFile = File(...),
#      db: Session = Depends(get_db)
     
# ):
#     db_event = db.query(Event).filter(Event.id == event_id).first()
#     if not db_event:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Event with id {event_id} not found"
#         )
    
#     try:
#         # Create directory if not exists
#         upload_dir = os.path.join(settings.upload_dir, 'events')
#         os.makedirs(upload_dir, exist_ok=True)
        
#         # Generate unique filename
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         file_extension = os.path.splitext(file.filename)[1]
#         filename = f"event_{event_id}_{timestamp}{file_extension}"
#         file_location = os.path.join(upload_dir, filename)
        
#         # Delete old image if exists
#         if db_event.image_url and os.path.exists(db_event.image_url):
#             os.remove(db_event.image_url)
        
#         # Save new file
#         with open(file_location, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
        
#         # Update database
#         db_event.image_url = file_location
#         db.commit()
#         db.refresh(db_event)
        
#         return {
#             "message": "Image uploaded successfully",
#             "location": file_location,
#             "content_type": file.content_type
#         }
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to upload image: {str(e)}"
#         )