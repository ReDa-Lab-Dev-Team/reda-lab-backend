from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, desc, asc

from app.config.database import get_db
from app.schemas.lab_entities import ResearchClubCreate, ResearchClubResponse, ResearchClubUpdate
from app.models.lab_entities import ResearchClub

router = APIRouter(prefix="/research-clubs", tags=["Admin - Research Clubs"])

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
    """Get all research clubs with pagination and filters (Admin only)"""
    try:
        query = db.query(ResearchClub)

        if search:
            query = query.filter(
                or_(
                    ResearchClub.name.ilike(f"%{search}%"),
                    ResearchClub.description.ilike(f"%{search}%"),
                    ResearchClub.core_theme.ilike(f"%{search}%"),
                    ResearchClub.leaders.ilike(f"%{search}%")
                )
            )

        if is_active is not None:
            query = query.filter(ResearchClub.is_active == is_active)

        order_func = desc if order == "desc" else asc
        query = query.order_by(order_func(getattr(ResearchClub, sort_by)))
        
        # Apply pagination
        clubs = query.offset(skip).limit(limit).all()
        return clubs
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve research clubs"
        )

@router.get("/{club_id}", response_model=ResearchClubResponse)
async def get_research_club(
    club_id: int,
     db: Session = Depends(get_db)
     
):
    """Get a single research club by ID (Admin only)"""
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
    club: ResearchClubCreate,
     db: Session = Depends(get_db)
     
):
    """Create a new research club (Admin only)"""
    try:
        current_admin = request.state.user
        db_club = ResearchClub(**club.model_dump(exclude_unset=True), created_by=current_admin.id)
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
    club: ResearchClubUpdate,
     db: Session = Depends(get_db)
     
):
    """Update an existing research club (Admin only)"""
    db_club = db.query(ResearchClub).filter(ResearchClub.id == club_id).first()
    if not db_club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Research club with id {club_id} not found"
        )
    
    try:
        for key, value in club.model_dump(exclude_unset=True).items():
            setattr(db_club, key, value)
        
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
    """Delete a research club (Admin only)"""
    db_club = db.query(ResearchClub).filter(ResearchClub.id == club_id).first()
    if not db_club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Research club with id {club_id} not found"
        )
    
    try:
        db.delete(db_club)
        db.commit()
        return {"message": "Research club deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete research club"
        )