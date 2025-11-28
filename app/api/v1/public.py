from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.sql import func

from app.config.database import get_db
from app.schemas.lab_entities import (
    ResearchProject, Publication, Event, TeamMember,
    AdvisoryBoardMember, News
)
from app.models.lab_entities import (
    ResearchProject as ResearchProjectModel,
    Publication as PublicationModel,
    Event as EventModel,
    TeamMember as TeamMemberModel,
    AdvisoryBoardMember as AdvisoryBoardMemberModel,
    News as NewsModel
)

router = APIRouter(prefix="/public", tags=["Public Content"])


@router.get("/projects", response_model=List[ResearchProject])
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ResearchProjectModel)
    if status:
        query = query.filter(ResearchProjectModel.status == status)
    projects = query.offset(skip).limit(limit).all()
    return projects


@router.get("/publications", response_model=List[Publication])
async def get_publications(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(PublicationModel).filter(
        PublicationModel.is_published == True)
    if year:
        query = query.filter(func.extract(
            'year', PublicationModel.publication_date) == year)
    publications = query.offset(skip).limit(limit).all()
    return publications


@router.get("/events", response_model=List[Event])
async def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    upcoming: bool = True,
    db: Session = Depends(get_db)
):
    from datetime import datetime
    query = db.query(EventModel).filter(EventModel.is_active == True)
    if upcoming:
        query = query.filter(EventModel.start_datetime >= datetime.now())
    else:
        query = query.filter(EventModel.start_datetime < datetime.now())
    events = query.order_by(EventModel.start_datetime.desc()).offset(
        skip).limit(limit).all()
    return events


@router.get("/team", response_model=List[TeamMember])
async def get_team_members(
    role: Optional[str] = None,
    active: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(TeamMemberModel).filter(
        TeamMemberModel.is_active == active)
    if role:
        query = query.filter(TeamMemberModel.position.contains(role))
    members = query.all()
    return members


@router.get("/news", response_model=List[News])
async def get_news(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    news = db.query(NewsModel).filter(NewsModel.is_published == True).order_by(
        NewsModel.published_date.desc()
    ).offset(skip).limit(limit).all()
    return news
