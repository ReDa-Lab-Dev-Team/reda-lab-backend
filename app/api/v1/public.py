from sqlalchemy.orm import Session
from typing import Optional, List
from app.config.database import get_db
from fastapi import Query,Depends
from app.schemas.lab_entities import AdvisoryBoardMemberResponse, EventResponse, EventType, NewsResponse, ResearchProjectResponse, ProjectStatus, ResearchClubResponse, TeamMemberResponse, ResearchPaperResponse, PaperType
from fastapi import APIRouter, Depends, Query
from app.services.public import UserService

router = APIRouter(prefix="/public", tags=["Public"])
service = UserService()


@router.get("/advisory-members", response_model=List[AdvisoryBoardMemberResponse])
async def get_advisory_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_by: str = Query("created_at", pattern="^(name|position|institution|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
     db: Session = Depends(get_db)
     
):
    return await service.get_advisory_members(skip, limit, search, is_active, sort_by, order, db)
 
@router.get("/events", response_model=List[EventResponse])
async def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    event_type: Optional[EventType] = None,
    is_active: Optional[bool] = None,
    sort_by: str = Query("created_at", pattern="^(title|start_datetime|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
     db: Session = Depends(get_db)
     
):
    return await service.get_events(skip, limit, search, event_type, is_active, sort_by, order, db)

@router.get("/news", response_model=List[NewsResponse])
async def get_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    is_published: Optional[bool] = None,
    sort_by: str = Query("created_at", pattern="^(title|published_date|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
     db: Session = Depends(get_db)
     
):
    return await service.get_news(skip, limit, search, is_published, sort_by, order, db)

@router.get("/projects", response_model=List[ResearchProjectResponse])
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    project_status: Optional[ProjectStatus] = Query(None, alias="status"),
    category_id: Optional[int] = None,
    sort_by: str = Query("created_at", pattern="^(title|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
     db: Session = Depends(get_db)
     
):
    status_value = project_status.value if project_status else None
    return await service.get_projects(skip, limit, search, status_value, category_id, sort_by, order, db)

@router.get("/research-clubs", response_model=List[ResearchClubResponse])
async def get_research_clubs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_by: str = Query("created_at", pattern="^(name|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
     db: Session = Depends(get_db)
     
):
    return await service.get_research_clubs(skip, limit, search, is_active, sort_by, order, db)

@router.get("/team-members", response_model=List[TeamMemberResponse])
async def get_team_members(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    sort_by: str = Query("created_at", pattern="^(name|position|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
     db: Session = Depends(get_db)
     
):
    return await service.get_team_members(skip, limit, search, is_active, sort_by, order, db)

@router.get("/research-papers", response_model=List[ResearchPaperResponse])
async def get_research_papers(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    paper_type: Optional[PaperType] = None,
    is_published: Optional[bool] = None,
    sort_by: str = Query("created_at", pattern="^(title|published_date|created_at|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
     db: Session = Depends(get_db)
     
):
    paper_type_value = paper_type.value if paper_type else None
    return await service.get_research_papers(skip, limit, search, paper_type_value, is_published, sort_by, order, db)
