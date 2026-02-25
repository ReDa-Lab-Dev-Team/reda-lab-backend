from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, desc, asc
from app.utils.helper_functions import slugify
from app.config.database import get_db
from app.utils.oauth2 import get_current_user
from app.models.admin import Admin
from app.schemas.lab_entities import ResearchProjectCreate, ResearchProjectResponse, ProjectStatus, ResearchProjectUpdate
from app.models.lab_entities import ResearchProject, Category, TeamMember

router = APIRouter(prefix="/projects", tags=["Admin - Research Projects"])

# ========== READ OPERATIONS ==========

@router.get("", response_model=List[ResearchProjectResponse])
async def get_all_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    project_status: Optional[ProjectStatus] = Query(None, description="Filter by project status", alias="status"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    sort_by: str = Query("created_at", pattern="^(title|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)#, current_admin: Admin = Depends(get_current_user)
):
    """Get all research projects with pagination and filters (Admin only)"""
    try:
        query = db.query(ResearchProject).filter(ResearchProject.is_deleted == False)

        # Apply filters
        if search:
            query = query.filter(
                or_(
                    ResearchProject.title.ilike(f"%{search}%"),
                    ResearchProject.description.ilike(f"%{search}%")
                )
            )

        if project_status:
            query = query.filter(ResearchProject.status == project_status.value)

        if category_id:
            query = query.join(ResearchProject.categories).filter(Category.id == category_id)

        # Apply sorting
        order_func = desc if order == "desc" else asc
        query = query.order_by(order_func(getattr(ResearchProject, sort_by)))
        
        # Apply pagination
        projects = query.offset(skip).limit(limit).all()
        
        print("Project: ", projects[0])
        return projects
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )


@router.get("/{project_id}", response_model=ResearchProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Get a single research project by ID (Admin only)"""
    db_project = db.query(ResearchProject).filter(
        ResearchProject.id == project_id,
        ResearchProject.is_deleted == False
    ).first()
    
    if not db_project:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    return db_project

# ========== CREATE OPERATION ==========

@router.post("", response_model=ResearchProjectResponse, status_code=http_status.HTTP_201_CREATED)
async def create_project(
    project: ResearchProjectCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Create a new research project (Admin only)"""
    try:
        # Convert Pydantic model to dictionary
        project_data = project.model_dump(exclude_unset=True)
        
        # Auto-generate slug if not provided
        if not project_data.get("slug"):
            project_data["slug"] = slugify(project.title)
        
        # Check if slug already exists
        existing_project = db.query(ResearchProject).filter(
            ResearchProject.slug == project_data["slug"],
            ResearchProject.is_deleted == False
        ).first()
        
        if existing_project:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Project with slug '{project_data['slug']}' already exists"
            )
        
        # Extract relationship IDs (not actual model fields)
        contributor_ids = project_data.pop('contributor_ids', [])
        category_ids = project_data.pop('category_ids', [])
        
        # Create project instance
        db_project = ResearchProject(**project_data, created_by=current_admin.id)
        
        # Handle many-to-many relationships
        if contributor_ids:
            contributors = db.query(TeamMember).filter(
                TeamMember.id.in_(contributor_ids),
                TeamMember.is_deleted == False
            ).all()
            
            if len(contributors) != len(contributor_ids):
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="One or more contributor IDs are invalid"
                )
            db_project.contributors = contributors
        
        if category_ids:
            categories = db.query(Category).filter(
                Category.id.in_(category_ids),
                Category.is_deleted == False
            ).all()
            
            if len(categories) != len(category_ids):
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="One or more category IDs are invalid"
                )
            db_project.categories = categories
        
        # Save to database
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        return db_project
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Project already exists or violates unique constraint"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


# ========== UPDATE OPERATION ==========

@router.put("/{project_id}", response_model=ResearchProjectResponse)
async def update_project(
    project_id: int,
    project: ResearchProjectUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
):
    """Update an existing research project (Admin only)"""
    # Find existing project
    db_project = db.query(ResearchProject).filter(
        ResearchProject.id == project_id,
        ResearchProject.is_deleted == False
    ).first()
    
    if not db_project:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    try:
        # Convert to dict and handle slug
        project_data = project.model_dump(exclude_unset=True)
        
        # If title changed and slug not provided, regenerate slug
        if "title" in project_data and not project_data.get("slug"):
            project_data["slug"] = slugify(project_data["title"])
        
        # Check slug uniqueness (if changed)
        if "slug" in project_data and project_data["slug"] != db_project.slug:
            existing_project = db.query(ResearchProject).filter(
                ResearchProject.slug == project_data["slug"],
                ResearchProject.id != project_id,
                ResearchProject.is_deleted == False
            ).first()
            
            if existing_project:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=f"Project with slug '{project_data['slug']}' already exists"
                )
        
        # Extract relationship IDs
        contributor_ids = project_data.pop('contributor_ids', None)
        category_ids = project_data.pop('category_ids', None)
        
        # Update basic fields
        for key, value in project_data.items():
            setattr(db_project, key, value)
        # Update relationships ONLY if explicitly provided
        if contributor_ids is not None:
            if len(contributor_ids) > 0:
                contributors = db.query(TeamMember).filter(
                    TeamMember.id.in_(contributor_ids),
                    TeamMember.is_deleted == False
                ).all()
                
                if len(contributors) != len(contributor_ids):
                    raise HTTPException(
                        status_code=http_status.HTTP_400_BAD_REQUEST,
                        detail="One or more contributor IDs are invalid"
                    )
                db_project.contributors = contributors
            else:
                # Empty list means clear all contributors
                db_project.contributors = []
        
        if category_ids is not None:
            if len(category_ids) > 0:
                categories = db.query(Category).filter(
                    Category.id.in_(category_ids),
                    Category.is_deleted == False
                ).all()
                
                if len(categories) != len(category_ids):
                    raise HTTPException(
                        status_code=http_status.HTTP_400_BAD_REQUEST,
                        detail="One or more category IDs are invalid"
                    )
                db_project.categories = categories
            else:
                # Empty list means clear all categories
                db_project.categories = []
        
        db.commit()
        db.refresh(db_project)
        return db_project
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Update violates unique constraint"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


# ========== DELETE OPERATION ==========

@router.delete("/{project_id}", status_code=http_status.HTTP_200_OK)
async def delete_project(
    project_id: int,
    hard_delete: bool = Query(False, description="Permanently delete (true) or soft delete (false)"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete a research project - soft delete by default (Admin only)"""
    db_project = db.query(ResearchProject).filter(
        ResearchProject.id == project_id,
        ResearchProject.is_deleted == False
    ).first()
    
    if not db_project:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    try:
        if hard_delete:
            # Permanent deletion
            db.delete(db_project)
            message = "Project permanently deleted successfully"
        else:
            # Soft deletion
            db_project.is_deleted = True
            message = "Project soft deleted successfully"
        
        db.commit()
        return {"message": message}
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )