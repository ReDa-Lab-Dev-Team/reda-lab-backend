from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, desc, asc

from app.config.database import get_db
from app.utils.oauth2 import get_current_user
from app.models.admin import Admin
from app.schemas.lab_entities import AdvisoryBoardMemberCreate, AdvisoryBoardMemberResponse
from app.models.lab_entities import AdvisoryBoardMember

router = APIRouter(prefix="/advisory-board", tags=["Admin - Advisory Board"])

# ========== READ OPERATIONS ==========

@router.get("", response_model=List[AdvisoryBoardMemberResponse])
async def get_all_advisory_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    # expertise_area: Optional[str] = None,
    is_active: Optional[bool] = None,
    status: Optional[str] = None,
    sort_by: str = Query("created_at", pattern="^(name|position|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Get all advisory board members with pagination and filters (Admin only)"""
    try:
        query = db.query(AdvisoryBoardMember)

        if search:
            query = query.filter(
                or_(
                    AdvisoryBoardMember.name.ilike(f"%{search}%"),
                    AdvisoryBoardMember.position.ilike(f"%{search}%"),
                    AdvisoryBoardMember.institution.ilike(f"%{search}%"),
                    AdvisoryBoardMember.expertise.ilike(f"%{search}%")
                )
            )

        if is_active is not None:
            query = query.filter(AdvisoryBoardMember.is_active == is_active)

        order_func = desc if order == "desc" else asc
        query = query.order_by(order_func(getattr(AdvisoryBoardMember, sort_by)))
        
        # Apply pagination
        members = query.offset(skip).limit(limit).all()
        return members
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve advisory board members"
        )

@router.get("/{member_id}", response_model=AdvisoryBoardMemberResponse)
async def get_advisory_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Get a single advisory board member by ID (Admin only)"""
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
    member: AdvisoryBoardMemberCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Create a new advisory board member (Admin only)"""
    try:
        db_member = AdvisoryBoardMember(**member.model_dump(exclude_unset=True),created_by=current_admin.id)
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member
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
    member: AdvisoryBoardMemberCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Update an existing advisory board member (Admin only)"""
    db_member = db.query(AdvisoryBoardMember).filter(AdvisoryBoardMember.id == member_id).first()
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Advisory board member with id {member_id} not found"
        )
    
    try:
        for key, value in member.model_dump(exclude_unset=True).items():
            setattr(db_member, key, value)
        
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
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete an advisory board member (Admin only)"""
    db_member = db.query(AdvisoryBoardMember).filter(AdvisoryBoardMember.id == member_id).first()
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Advisory board member with id {member_id} not found"
        )
    
    try:
        db.delete(db_member)
        db.commit()
        return {"message": "Advisory board member deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete advisory board member"
        )