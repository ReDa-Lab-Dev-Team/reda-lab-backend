from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.utils.auth import get_current_admin_user
from app.models.user import User
from app.schemas.lab_entities import (
    ResearchProjectCreate, ResearchProject, PublicationCreate, 
    Publication, EventCreate, Event, TeamMemberCreate, TeamMember
)
from app.models.lab_entities import ResearchProject as ResearchProjectModel

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

@router.post("/projects", response_model=ResearchProject)
async def create_project(
    project: ResearchProjectCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_project = ResearchProjectModel(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.put("/projects/{project_id}", response_model=ResearchProject)
async def update_project(
    project_id: int,
    project: ResearchProjectCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_project = db.query(ResearchProjectModel).filter(ResearchProjectModel.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in project.dict().items():
        setattr(db_project, key, value)
    
    db.commit()
    return db_project

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_project = db.query(ResearchProjectModel).filter(ResearchProjectModel.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}