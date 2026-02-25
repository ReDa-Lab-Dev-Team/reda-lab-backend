from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, desc, asc
import os
import shutil
from datetime import datetime

from app.config.database import get_db
from app.utils.oauth2 import get_current_user
from app.models.admin import Admin
from app.schemas.lab_entities import EventCreate, EventResponse, EventUpdate
from app.models.lab_entities import Event, EventType
from app.config.config import settings

router = APIRouter(prefix="/events", tags=["Admin - Events"])

# ========== READ OPERATIONS ==========

@router.get("", response_model=List[EventResponse])
async def get_all_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    event_type: Optional[EventType] = None,
    is_active: Optional[bool] = None,
    sort_by: str = Query("start_datetime", pattern="^(title|start_datetime|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Get all events with pagination and filters (Admin only)"""
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
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Get a single event by ID (Admin only)"""
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
    event: EventCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Create a new event (Admin only)"""
    try:
        db_event = Event(**event.model_dump(exclude_unset=True), created_by=current_admin.id)
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
    event: EventUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Update an existing event (Admin only)"""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Event with id {event_id} not found"
        )
    
    try:
        for key, value in event.model_dump(exclude_unset=True).items():
            setattr(db_event, key, value)
        
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
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete an event (Admin only)"""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Event with id {event_id} not found"
        )
    
    try:
        # Delete associated image if exists
        if db_event.image_url and os.path.exists(db_event.image_url):
            os.remove(db_event.image_url)
        
        db.delete(db_event)
        db.commit()
        return {"message": "Event deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete event"
        )

# ========== FILE UPLOAD ==========

@router.post("/{event_id}/upload-image")
async def upload_event_image(
    event_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Upload event image (Admin only)"""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with id {event_id} not found"
        )
    
    try:
        # Create directory if not exists
        upload_dir = os.path.join(settings.upload_dir, 'events')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"event_{event_id}_{timestamp}{file_extension}"
        file_location = os.path.join(upload_dir, filename)
        
        # Delete old image if exists
        if db_event.image_url and os.path.exists(db_event.image_url):
            os.remove(db_event.image_url)
        
        # Save new file
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update database
        db_event.image_url = file_location
        db.commit()
        db.refresh(db_event)
        
        return {
            "message": "Image uploaded successfully",
            "location": file_location,
            "content_type": file.content_type
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )