from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, desc, asc

from app.config.database import get_db
from app.utils.oauth2 import get_current_user
from app.models.admin import Admin
from app.schemas.lab_entities import TeamMemberCreate, TeamMemberResponse
from app.models.lab_entities import TeamMember

router = APIRouter(prefix="/team-members", tags=["Admin - Team Members"])

# ========== READ OPERATIONS ==========

@router.get("", response_model=List[TeamMemberResponse])
async def get_all_team_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = Query("created_at", pattern="^(name|position|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Get all team members with pagination and filters (Admin only)"""
    try:
        query = db.query(TeamMember)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    TeamMember.name.ilike(f"%{search}%"),
                    TeamMember.position.ilike(f"%{search}%"),
                    TeamMember.bio.ilike(f"%{search}%")
                )
            )
        
        if role:
            query = query.filter(TeamMember.role == role)
        
        if department:
            query = query.filter(TeamMember.department == department)
        
        if status:
            query = query.filter(TeamMember.status == status)
        
        # Apply sorting
        order_func = desc if order == "desc" else asc
        if sort_by == "name":
            query = query.order_by(order_func(TeamMember.name))
        elif sort_by == "position":
            query = query.order_by(order_func(TeamMember.position))
        elif sort_by == "updated_at":
            query = query.order_by(order_func(TeamMember.updated_at))
        else:
            query = query.order_by(order_func(TeamMember.created_at))
        
        # Apply pagination
        members = query.offset(skip).limit(limit).all()
        return members
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve team members"
        )

@router.get("/{member_id}", response_model=TeamMemberResponse)
async def get_team_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Get a single team member by ID (Admin only)"""
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
    member: TeamMemberCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Create a new team member (Admin only)"""
    try:
        db_member = TeamMember(**member.model_dump(exclude_unset=True))
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
    member: TeamMemberCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Update an existing team member (Admin only)"""
    db_member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Team member with id {member_id} not found"
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
async def delete_team_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete a team member (Admin only)"""
    db_member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Team member with id {member_id} not found"
        )
    
    try:
        db.delete(db_member)
        db.commit()
        return {"message": "Team member deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete team member"
        )