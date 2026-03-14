from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, File, UploadFile,Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, desc, asc
import os
import shutil
from datetime import datetime
from app.utils.helper_functions import slugify
from app.config.database import get_db
from app.schemas.lab_entities import ResearchProjectCreate, ResearchProjectResponse, ProjectStatus, ResearchProjectUpdate
from app.models.lab_entities import ResearchProject, Category, TeamMember
from app.config.config import settings

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
    db: Session = Depends(get_db)#,  
):
    try:
        query = db.query(ResearchProject)

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
        return projects
        
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )


@router.get("/{project_id}", response_model=ResearchProjectResponse)
async def get_project(
    project_id: int,
     db: Session = Depends(get_db)
     
):
    db_project = db.query(ResearchProject).filter(
        ResearchProject.id == project_id
    ).first()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    return db_project

# ========== CREATE OPERATION ==========

@router.post("", response_model=ResearchProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: Request,
    project: ResearchProjectCreate = Depends(ResearchProjectCreate.as_form),
    image_url: Optional[UploadFile] = File(None),
     db: Session = Depends(get_db)
     
):
    try:
        current_admin = request.state.user
        
        # Convert Pydantic model to dictionary
        project_data = project.model_dump(exclude_unset=True)
        project_data["slug"] = slugify(project.title)
        
        # Check if slug already exists
        existing_project = db.query(ResearchProject).filter(
            ResearchProject.slug == project_data["slug"]
        ).first()
        
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project already exists"
            )
        if image_url:
            # Validate file type
            allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
            if image_url.content_type not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image type. Allowed types: jpeg, png, jpg, webp"
                )

            # Create upload directory
            path = os.path.join(settings.upload_dir, "projects")
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                    
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_ext = os.path.splitext(image_url.filename)[1]
            filename = f"{project_data['slug']}_{timestamp}{file_ext}"
            file_location = os.path.join(path, filename)
            
            # Save file
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(image_url.file, buffer)
                
            # Store relative path in database
            relative_path = os.path.join('projects', filename)
            project_data["image_url"] = relative_path
        
        # Extract relationship IDs (not actual model fields)
        contributor_ids = project_data.pop('contributor_ids', [])
        category_ids = project_data.pop('category_ids', [])
        
        # Create project instance
        db_project = ResearchProject(**project_data, created_by=current_admin.id)
        
        # Handle many-to-many relationships
        if contributor_ids:
            contributors = db.query(TeamMember).filter(
                TeamMember.id.in_(contributor_ids)
            ).all()
            
            if len(contributors) != len(contributor_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more contributor IDs are invalid"
                )
            db_project.contributors = contributors
        
        if category_ids:
            categories = db.query(Category).filter(
                Category.id.in_(category_ids)
            ).all()
            
            if len(categories) != len(category_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project already exists or violates unique constraint"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


# ========== UPDATE OPERATION ==========

@router.put("/{project_id}", response_model=ResearchProjectResponse)
async def update_project(
    project_id: int,
    project: ResearchProjectUpdate = Depends(ResearchProjectUpdate.as_form),
    image_url: Optional[UploadFile] = File(None),
     db: Session = Depends(get_db)
     
):
    # Find existing project
    db_project = db.query(ResearchProject).filter(
        ResearchProject.id == project_id
    ).first()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found"
        )
    
    try:
        # Convert to dict and handle slug
        project_data = project.model_dump(exclude_unset=True, exclude_none=True)
        
        # Only update slug if title is provided and not None
        if "title" in project_data and project_data["title"]:
            new_slug = slugify(project_data["title"])
            
            # Check slug uniqueness (if changed)
            if new_slug != db_project.slug:
                existing_project = db.query(ResearchProject).filter(
                    ResearchProject.slug == new_slug,
                    ResearchProject.id != project_id
                ).first()
                
                if existing_project:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Project with the same title already exists"
                    )
                project_data["slug"] = new_slug
        
        # Extract relationship IDs
        contributor_ids = project_data.pop('contributor_ids', None)
        category_ids = project_data.pop('category_ids', None)
        
        # Update basic fields
        for key, value in project_data.items():
            setattr(db_project, key, value)
        
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
                if db_project.image_url:
                    old_image_path = os.path.join(settings.upload_dir, db_project.image_url)
                    if os.path.exists(old_image_path):
                        try:
                            os.remove(old_image_path)
                        except Exception as e:
                            print(f"Warning: Could not delete old image: {e}")
                
                # Create upload directory
                path = os.path.join(settings.upload_dir, 'projects')
                if not os.path.exists(path):
                    os.makedirs(path, exist_ok=True)
                
                # Create unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_ext = os.path.splitext(image_url.filename)[1]
                filename = f"{db_project.slug}_{timestamp}{file_ext}"
                file_location = os.path.join(path, filename)
                
                # Save file
                with open(file_location, "wb") as buffer:
                    shutil.copyfileobj(image_url.file, buffer)
                
                # Store relative path
                relative_path = os.path.join('projects', filename)
                db_project.image_url = relative_path
                
            except Exception as e:
                # Cleanup on error
                if 'file_location' in locals() and os.path.exists(file_location):
                    os.remove(file_location)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload image: {str(e)}"
                )
        
        # Update relationships ONLY if explicitly provided
        if contributor_ids is not None:
            if len(contributor_ids) > 0:
                contributors = db.query(TeamMember).filter(
                    TeamMember.id.in_(contributor_ids)
                ).all()
                
                if len(contributors) != len(contributor_ids):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="One or more contributor IDs are invalid"
                    )
                db_project.contributors = contributors
            else:
                # Empty list means clear all contributors
                db_project.contributors = []
        
        if category_ids is not None:
            if len(category_ids) > 0:
                categories = db.query(Category).filter(
                    Category.id.in_(category_ids)                     
                ).all()
                
                if len(categories) != len(category_ids):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Update violates unique constraint"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


# ========== DELETE OPERATION ==========

@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):

    db_project = db.query(ResearchProject).filter(
        ResearchProject.id == project_id
    ).first()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found"
        )
    
    try:
        # Delete associated image if it exists
        if db_project.image_url:
            image_path = os.path.join(settings.upload_dir, db_project.image_url)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Error deleting image: {e}")
        
        # Permanent deletion of the project
        db.delete(db_project)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )