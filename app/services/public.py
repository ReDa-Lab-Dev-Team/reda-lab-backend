from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, Query, status
from app.models.lab_entities import AdvisoryBoardMember, Event, News, ResearchProject, ResearchClub, TeamMember, ResearchPaper
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, desc, asc


class UserService:
    async def get_advisory_members(
        self,
        skip: int,
        limit: int,
        search: Optional[str],
        is_active: Optional[bool],
        sort_by: str,
        order: str,
        db: Session
    ):
        """Get all advisory board members with pagination and filters"""
        try:
            query = db.query(AdvisoryBoardMember)

            if search:
                query = query.filter(
                    or_(
                        AdvisoryBoardMember.name.ilike(f"%{search}%"),
                        AdvisoryBoardMember.position.ilike(f"%{search}%"),
                        AdvisoryBoardMember.institution.ilike(f"%{search}%"),
                        AdvisoryBoardMember.expertise.ilike(f"%{search}%"),
                        AdvisoryBoardMember.bio.ilike(f"%{search}%")
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
    
    async def get_events(
        self,
        skip: int,
        limit: int,
        search: Optional[str],
        event_type: Optional[str],
        is_active: Optional[bool],
        sort_by: str,
        order: str,
        db: Session
        ):
        try:
            query = db.query(Event)

            if search:
                query = query.filter(
                    or_(
                        Event.title.ilike(f"%{search}%"),
                        Event.description.ilike(f"%{search}%"),
                        Event.location.ilike(f"%{search}%")
                    )
                )

            if event_type:
                query = query.filter(Event.event_type == event_type)

            if is_active is not None:
                query = query.filter(Event.is_active == is_active)

            order_func = desc if order == "desc" else asc
            query = query.order_by(order_func(getattr(Event, sort_by)))
            
            # Apply pagination
            events = query.offset(skip).limit(limit).all()
            return events
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve events"
            )
    async def get_news(
        self,
        skip: int,
        limit: int,
        search: Optional[str],
        is_published: Optional[bool],
        sort_by: str,
        order: str,
        db: Session
    ):
        """Get all news with pagination and filters"""
        try:
            query = db.query(News)

            if search:
                query = query.filter(
                    or_(
                        News.title.ilike(f"%{search}%"),
                        News.summary.ilike(f"%{search}%"),
                        News.content.ilike(f"%{search}%")
                    )
                )

            if is_published is not None:
                query = query.filter(News.is_published == is_published)

            order_func = desc if order == "desc" else asc
            query = query.order_by(order_func(getattr(News, sort_by)))
            
            # Apply pagination
            news = query.offset(skip).limit(limit).all()
            return news
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve news"
            )

    async def get_projects(
        self,
        skip: int,
        limit: int,
        search: Optional[str],
        project_status: Optional[str],
        category_id: Optional[int],
        sort_by: str,
        order: str,
        db: Session
    ):
        """Get all research projects with pagination and filters"""
        try:
            query = db.query(ResearchProject)

            if search:
                query = query.filter(
                    or_(
                        ResearchProject.title.ilike(f"%{search}%"),
                        ResearchProject.description.ilike(f"%{search}%")
                    )
                )

            if project_status:
                query = query.filter(ResearchProject.status == project_status)

            if category_id:
                from app.models.lab_entities import Category
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

    async def get_research_clubs(
        self,
        skip: int,
        limit: int,
        search: Optional[str],
        is_active: Optional[bool],
        sort_by: str,
        order: str,
        db: Session
    ):
        """Get all research clubs with pagination and filters"""
        try:
            query = db.query(ResearchClub)

            if search:
                query = query.filter(
                    or_(
                        ResearchClub.name.ilike(f"%{search}%"),
                        ResearchClub.description.ilike(f"%{search}%"),
                        ResearchClub.core_theme.ilike(f"%{search}%"),
                        ResearchClub.leaders.ilike(f"%{search}%")
                    )
                )

            if is_active is not None:
                query = query.filter(ResearchClub.is_active == is_active)

            order_func = desc if order == "desc" else asc
            query = query.order_by(order_func(getattr(ResearchClub, sort_by)))
            
            # Apply pagination
            clubs = query.offset(skip).limit(limit).all()
            return clubs
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve research clubs"
            )

    async def get_team_members(
        self,
        skip: int,
        limit: int,
        search: Optional[str],
        is_active: Optional[bool],
        sort_by: str,
        order: str,
        db: Session
    ):
        """Get all team members with pagination and filters"""
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

    async def get_research_papers(
        self,
        skip: int,
        limit: int,
        search: Optional[str],
        paper_type: Optional[str],
        is_published: Optional[bool],
        sort_by: str,
        order: str,
        db: Session
    ):
        """Get all research papers with pagination and filters"""
        try:
            query = db.query(ResearchPaper)

            if search:
                query = query.filter(
                    or_(
                        ResearchPaper.title.ilike(f"%{search}%"),
                        ResearchPaper.abstract.ilike(f"%{search}%"),
                        ResearchPaper.authors.ilike(f"%{search}%")
                    )
                )

            if paper_type:
                query = query.filter(ResearchPaper.paper_type == paper_type)

            if is_published is not None:
                query = query.filter(ResearchPaper.is_published == is_published)

            order_func = desc if order == "desc" else asc
            query = query.order_by(order_func(getattr(ResearchPaper, sort_by)))
            
            # Apply pagination
            papers = query.offset(skip).limit(limit).all()
            return papers
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve research papers"
            )
    