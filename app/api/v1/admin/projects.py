from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, desc, asc

from app.config.database import get_db
from app.utils.oauth2 import get_current_user
from app.models.admin import Admin
from app.schemas.lab_entities import ResearchProjectCreate, ResearchProjectResponse
from app.models.lab_entities import ResearchProject, Category

router = APIRouter(prefix="/projects", tags=["Admin - Research Projects"])

# ========== READ OPERATIONS ==========

@router.get("", response_model=List[ResearchProjectResponse])
async def get_all_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    sort_by: str = Query("created_at", pattern="^(title|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Get all research projects with pagination and filters (Admin only)"""
    try:
        query = db.query(ResearchProject)

        if search:
            query = query.filter(
                or_(
                    ResearchProject.title.ilike(f"%{search}%"),
                    ResearchProject.description.ilike(f"%{search}%")
                )
            )

        if status:
            query = query.filter(ResearchProject.status == status)

        if category_id:
            query = query.join(ResearchProject.categories).filter(Category.id == category_id)

        order_func = desc if order == "desc" else asc
        query = query.order_by(order_func(getattr(ResearchProject, sort_by)))
        
        # Apply pagination
        projects = query.offset(skip).limit(limit).all()
        return projects
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )

@router.get("/{project_id}", response_model=ResearchProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Get a single research project by ID (Admin only)"""
    db_project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    return db_project

# ========== CREATE OPERATION ==========

@router.post("", response_model=ResearchProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ResearchProjectCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Create a new research project (Admin only)"""
    try:
        db_project = ResearchProject(**project.model_dump(exclude_unset=True),created_by=current_admin.id)
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Project already exists or violates unique constraint"
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Database error occurred"
        )

# ========== UPDATE OPERATION ==========

@router.put("/{project_id}", response_model=ResearchProjectResponse)
async def update_project(
    project_id: int,
    project: ResearchProjectCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Update an existing research project (Admin only)"""
    db_project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Project with id {project_id} not found"
        )
    
    try:
        for key, value in project.model_dump(exclude_unset=True).items():
            setattr(db_project, key, value)
        
        db.commit()
        db.refresh(db_project)
        return db_project
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

@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete a research project (Admin only)"""
    db_project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Project with id {project_id} not found"
        )
    
    try:
        db.delete(db_project)
        db.commit()
        return {"message": "Project deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete project"
        )