from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, desc, asc

from app.config.database import get_db
from app.utils.oauth2 import get_current_user
from app.models.admin import Admin
from app.schemas.lab_entities import PublicationCreate, PublicationResponse
from app.models.lab_entities import Publication

router = APIRouter(prefix="/publications", tags=["Admin - Publications"])

# ========== READ OPERATIONS ==========

@router.get("", response_model=List[PublicationResponse])
async def get_all_publications(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    year: Optional[int] = None,
    publication_type: Optional[str] = None,
    category_id: Optional[int] = None,
    sort_by: str = Query("created_at", pattern="^(title|year|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Get all publications with pagination and filters (Admin only)"""
    try:
        query = db.query(Publication)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    Publication.title.ilike(f"%{search}%"),
                    Publication.authors.ilike(f"%{search}%"),
                    Publication.abstract.ilike(f"%{search}%")
                )
            )
        
        if year:
            query = query.filter(Publication.year == year)
        
        if publication_type:
            query = query.filter(Publication.publication_type == publication_type)
        
        if category_id:
            query = query.filter(Publication.category_id == category_id)
        
        # Apply sorting
        order_func = desc if order == "desc" else asc
        if sort_by == "title":
            query = query.order_by(order_func(Publication.title))
        elif sort_by == "year":
            query = query.order_by(order_func(Publication.year))
        elif sort_by == "updated_at":
            query = query.order_by(order_func(Publication.updated_at))
        else:
            query = query.order_by(order_func(Publication.created_at))
        
        # Apply pagination
        publications = query.offset(skip).limit(limit).all()
        return publications
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve publications"
        )

@router.get("/{publication_id}", response_model=PublicationResponse)
async def get_publication(
    publication_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Get a single publication by ID (Admin only)"""
    db_publication = db.query(Publication).filter(Publication.id == publication_id).first()
    if not db_publication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Publication with id {publication_id} not found"
        )
    return db_publication

# ========== CREATE OPERATION ==========

@router.post("", response_model=PublicationResponse, status_code=status.HTTP_201_CREATED)
async def create_publication(
    publication: PublicationCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Create a new publication (Admin only)"""
    try:
        db_publication = Publication(**publication.model_dump(exclude_unset=True))
        db.add(db_publication)
        db.commit()
        db.refresh(db_publication)
        return db_publication
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Publication already exists or violates unique constraint"
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error occurred"
        )

# ========== UPDATE OPERATION ==========

@router.put("/{publication_id}", response_model=PublicationResponse)
async def update_publication(
    publication_id: int,
    publication: PublicationCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Update an existing publication (Admin only)"""
    db_publication = db.query(Publication).filter(Publication.id == publication_id).first()
    if not db_publication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Publication with id {publication_id} not found"
        )
    
    try:
        for key, value in publication.model_dump(exclude_unset=True).items():
            setattr(db_publication, key, value)
        
        db.commit()
        db.refresh(db_publication)
        return db_publication
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

@router.delete("/{publication_id}", status_code=status.HTTP_200_OK)
async def delete_publication(
    publication_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete a publication (Admin only)"""
    db_publication = db.query(Publication).filter(Publication.id == publication_id).first()
    if not db_publication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Publication with id {publication_id} not found"
        )
    
    try:
        db.delete(db_publication)
        db.commit()
        return {"message": "Publication deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete publication"
        )