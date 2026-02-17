from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.utils.oauth2 import get_current_active_user
from app.models.admin import Admin
from app.schemas.admin import AdminResponse
from app.schemas.lab_entities import (
    ResearchProjectCreate, ResearchProjectResponse, PublicationCreate, 
    PublicationResponse, EventCreate, EventResponse, TeamMemberCreate, 
    TeamMemberResponse, NewsCreate, NewsResponse, AdvisoryBoardMemberCreate,
    AdvisoryBoardMemberResponse, CategoryCreate, CategoryResponse
)
from app.models.lab_entities import (
    ResearchProject, Publication, Event, TeamMember, News, 
    AdvisoryBoardMember, Category
)

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

# ========== RESEARCH PROJECTS ==========

@router.post("/projects", response_model=ResearchProjectResponse)
async def create_project(
    project: ResearchProjectCreate,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_project = ResearchProject(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.put("/projects/{project_id}", response_model=ResearchProjectResponse)
async def update_project(
    project_id: int,
    project: ResearchProjectCreate,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in project.model_dump().items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}

# ========== PUBLICATIONS ==========

@router.post("/publications", response_model=PublicationResponse)
async def create_publication(
    publication: PublicationCreate,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_publication = Publication(**publication.model_dump())
    db.add(db_publication)
    db.commit()
    db.refresh(db_publication)
    return db_publication

@router.put("/publications/{publication_id}", response_model=PublicationResponse)
async def update_publication(
    publication_id: int,
    publication: PublicationCreate,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_publication = db.query(Publication).filter(Publication.id == publication_id).first()
    if not db_publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    for key, value in publication.model_dump().items():
        setattr(db_publication, key, value)
    
    db.commit()
    db.refresh(db_publication)
    return db_publication

@router.delete("/publications/{publication_id}")
async def delete_publication(
    publication_id: int,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_publication = db.query(Publication).filter(Publication.id == publication_id).first()
    if not db_publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    db.delete(db_publication)
    db.commit()
    return {"message": "Publication deleted successfully"}

# ========== EVENTS ==========

@router.post("/events", response_model=EventResponse)
async def create_event(
    event: EventCreate,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_event = Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.put("/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event: EventCreate,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    for key, value in event.model_dump().items():
        setattr(db_event, key, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event

@router.delete("/events/{event_id}")
async def delete_event(
    event_id: int,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(db_event)
    db.commit()
    return {"message": "Event deleted successfully"}

# ========== TEAM MEMBERS ==========

@router.post("/team-members", response_model=TeamMemberResponse)
async def create_team_member(
    member: TeamMemberCreate,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_member = TeamMember(**member.model_dump())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

@router.put("/team-members/{member_id}", response_model=TeamMemberResponse)
async def update_team_member(
    member_id: int,
    member: TeamMemberCreate,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    for key, value in member.model_dump().items():
        setattr(db_member, key, value)
    
    db.commit()
    db.refresh(db_member)
    return db_member

@router.delete("/team-members/{member_id}")
async def delete_team_member(
    member_id: int,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Team member not found")
    
    db.delete(db_member)
    db.commit()
    return {"message": "Team member deleted successfully"}

# ========== NEWS ==========

@router.post("/news", response_model=NewsResponse)
async def create_news(
    news: NewsCreate,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_news = News(**news.model_dump())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

@router.put("/news/{news_id}", response_model=NewsResponse)
async def update_news(
    news_id: int,
    news: NewsCreate,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_news = db.query(News).filter(News.id == news_id).first()
    if not db_news:
        raise HTTPException(status_code=404, detail="News not found")
    
    for key, value in news.model_dump().items():
        setattr(db_news, key, value)
    
    db.commit()
    db.refresh(db_news)
    return db_news

@router.delete("/news/{news_id}")
async def delete_news(
    news_id: int,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_news = db.query(News).filter(News.id == news_id).first()
    if not db_news:
        raise HTTPException(status_code=404, detail="News not found")
    
    db.delete(db_news)
    db.commit()
    return {"message": "News deleted successfully"}

# ========== ADVISORY BOARD ==========

@router.post("/advisory-board", response_model=AdvisoryBoardMemberResponse)
async def create_advisory_member(
    member: AdvisoryBoardMemberCreate,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_member = AdvisoryBoardMember(**member.model_dump())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

@router.put("/advisory-board/{member_id}", response_model=AdvisoryBoardMemberResponse)
async def update_advisory_member(
    member_id: int,
    member: AdvisoryBoardMemberCreate,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_member = db.query(AdvisoryBoardMember).filter(AdvisoryBoardMember.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Advisory board member not found")
    
    for key, value in member.model_dump().items():
        setattr(db_member, key, value)
    
    db.commit()
    db.refresh(db_member)
    return db_member

@router.delete("/advisory-board/{member_id}")
async def delete_advisory_member(
    member_id: int,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_member = db.query(AdvisoryBoardMember).filter(AdvisoryBoardMember.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Advisory board member not found")
    
    db.delete(db_member)
    db.commit()
    return {"message": "Advisory board member deleted successfully"}

# ========== CATEGORIES ==========

@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category: CategoryCreate,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    for key, value in category.model_dump().items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    current_admin: AdminResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(db_category)
    db.commit()
    return {"message": "Category deleted successfully"}