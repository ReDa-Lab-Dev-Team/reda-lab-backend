from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, desc, asc, func

from app.config.database import get_db
from app.utils.oauth2 import get_current_user
from app.models.admin import Admin
from app.schemas.lab_entities import TeamMemberCreate, TeamMemberResponse, TeamMemberUpdate
from app.models.lab_entities import TeamMember

router = APIRouter(prefix="/team-members", tags=["Admin - Team Members"])

# ========== READ OPERATIONS ==========

@router.get("/count", response_model=Dict[str, int])
async def count_team_members(
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Count total team members with optional filters (Admin only)"""
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
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user) 
):
    """Get all team members with pagination and filters (Admin only)"""
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

@router.get("/position/{position}", response_model=List[TeamMemberResponse])
async def get_team_members_by_position(
    position: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Get team members by position/role (Admin only)"""
    try:
        query = db.query(TeamMember).filter(TeamMember.position.ilike(f"%{position}%"))
        
        if is_active is not None:
            query = query.filter(TeamMember.is_active == is_active)
        
        members = query.offset(skip).limit(limit).all()
        
        if not members:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No team members found with position containing '{position}'"
            )
        
        return members
    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve team members by position"
        )

@router.get("/{member_id}", response_model=TeamMemberResponse)
async def get_team_member_id(
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
        db_member = TeamMember(**member.model_dump(exclude_unset=True),created_by=current_admin.id)
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
    member: TeamMemberUpdate,
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

@router.delete("/delete/{member_id}", status_code=status.HTTP_200_OK)
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
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete team member"
        )