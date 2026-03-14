from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, ValidationError
from typing import List, Optional
from datetime import datetime
from enum import Enum
from decimal import Decimal
from fastapi import Depends, Form, HTTPException, status
import json



# =========================================================
# ENUMS (Must Match Database Enums Exactly)
# =========================================================

class ProjectStatus(str, Enum):
    active = "active"
    completed = "completed"
    upcoming = "upcoming"
    paused = "paused"


class EventType(str, Enum):
    workshop = "workshop"
    seminar = "seminar"
    conference = "conference"
    meeting = "meeting"


class PaperType(str, Enum):
    journal = "journal"
    conference = "conference"
    workshop = "workshop"
    book_chapter = "book_chapter"
    thesis = "thesis"
    technical_report = "technical_report"
    preprint = "preprint"
    poster = "poster"

# =========================================================
# CATEGORY
# =========================================================

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating categories - all fields optional"""
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# TEAM MEMBER
# =========================================================

class TeamMemberBase(BaseModel):
    name: str
    position: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: bool = True
    image_url: Optional[str] = None   
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        if v and not v.endswith('@gmail.com'):
            raise ValueError('Email must be from @gmail.com domain')
        return v


class TeamMemberCreate(TeamMemberBase):
    
    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        position: Optional[str] = Form(None),
        bio: Optional[str] = Form(None),
        email: Optional[EmailStr] = Form(None),
        is_active: bool = Form(True)
    ):
        try:
            return cls(
                name=name,
                position=position,
                bio=bio,
                email=email,
                is_active=is_active
            )
        except ValidationError as e:
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', 'Validation error')
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"msg": error_msg}
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"msg": "Invalid input data"}
            )


class TeamMemberUpdate(BaseModel):
    """Schema for updating team members - all fields optional"""
    name: Optional[str] = None
    position: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    image_url: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        if v and not v.endswith('@gmail.com'):
            raise ValueError('Email must be from @gmail.com domain')
        return v
    
    @classmethod
    def as_form(
        cls,
        name: Optional[str] = Form(None),
        position: Optional[str] = Form(None),
        bio: Optional[str] = Form(None),
        email: Optional[EmailStr] = Form(None),
        is_active: Optional[bool] = Form(None)
    ):
        try:
            return cls(
                name=name,
                position=position,
                bio=bio,
                email=email,
                is_active=is_active
            )
        except ValidationError as e:
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', 'Validation error')
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"msg": error_msg}
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"msg": "Invalid input data"}
            )


class TeamMemberResponse(TeamMemberBase):
    id: int
    is_active: bool
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# RESEARCH PROJECT
# =========================================================

class ResearchProjectBase(BaseModel):
    title: str
    slug: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_featured: bool = False
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: ProjectStatus = ProjectStatus.active
    funding_source: Optional[str] = None
    budget: Optional[Decimal] = None


class ResearchProjectCreate(ResearchProjectBase):
    contributor_ids: List[int] = []
    category_ids: List[int] = []
    
    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: Optional[str] = Form(None),
        is_featured: bool = Form(False),
        start_date: Optional[datetime] = Form(None),
        end_date: Optional[datetime] = Form(None),
        status: ProjectStatus = Form(ProjectStatus.active),
        funding_source: Optional[str] = Form(None),
        budget: Optional[Decimal] = Form(None),
        contributor_ids: str = Form("[]"),
        category_ids: str = Form("[]")
    ):
        try:
            import json
            contributor_ids_list = json.loads(contributor_ids) if contributor_ids else []
            category_ids_list = json.loads(category_ids) if category_ids else []
            
            return cls(
                title=title,
                description=description,
                is_featured=is_featured,
                start_date=start_date,
                end_date=end_date,
                status=status,
                funding_source=funding_source,
                budget=budget,
                contributor_ids=contributor_ids_list,
                category_ids=category_ids_list
            )
        except ValidationError as e:
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', 'Validation error')
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"msg": error_msg}
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"msg": "Invalid input data"}
            )


class ResearchProjectUpdate(BaseModel):
    """Schema for updating research projects - all fields optional"""
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_featured: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[ProjectStatus] = None
    funding_source: Optional[str] = None
    budget: Optional[Decimal] = None
    contributor_ids: Optional[List[int]] = None
    category_ids: Optional[List[int]] = None
    
    @classmethod
    def as_form(
        cls,
        title: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        is_featured: Optional[bool] = Form(None),
        start_date: Optional[datetime] = Form(None),
        end_date: Optional[datetime] = Form(None),
        status: Optional[ProjectStatus] = Form(None),
        funding_source: Optional[str] = Form(None),
        budget: Optional[Decimal] = Form(None),
        contributor_ids: Optional[str] = Form(None),
        category_ids: Optional[str] = Form(None)
    ):
        try:
            
            contributor_ids_list = json.loads(contributor_ids) if contributor_ids else None
            category_ids_list = json.loads(category_ids) if category_ids else None
            
            return cls(
                title=title,
                description=description,
                is_featured=is_featured,
                start_date=start_date,
                end_date=end_date,
                status=status,
                funding_source=funding_source,
                budget=budget,
                contributor_ids=contributor_ids_list,
                category_ids=category_ids_list
            )
        except ValidationError as e:
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', 'Validation error')
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"msg": error_msg}
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"msg": "Invalid input data"}
            )


class ResearchProjectResponse(ResearchProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    contributors: List[TeamMemberResponse] = []
    categories: List[CategoryResponse] = []

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# RESEARCH CLUB
# =========================================================

class ResearchClubBase(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    core_theme: Optional[str] = None
    leaders: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True


class ResearchClubCreate(ResearchClubBase):
    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        description: Optional[str] = Form(None),
        core_theme: Optional[str] = Form(None),
        leaders: Optional[str] = Form(None)
        # image_url: Optional[str] = Form(None),
    ):
        try:
            return cls(
                name=name,
                description=description,
                core_theme=core_theme,
                leaders=leaders
                # image_url=image_url
            )
        except ValidationError as e:
            # Extract the error message
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', 'Validation error')
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"msg": error_msg}
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"msg": "Invalid input data"}
            )


class ResearchClubUpdate(BaseModel):

    name: Optional[str] = None
    description: Optional[str] = None
    core_theme: Optional[str] = None
    leaders: Optional[str] = None
    @classmethod
    def as_form(
        cls,
        name: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        core_theme: Optional[str] = Form(None),
        leaders: Optional[str] = Form(None)
        # image_url: Optional[str] = Form(None),
    ):
        try:
            return cls(
                name=name,
                description=description,
                core_theme=core_theme,
                leaders=leaders
                # image_url=image_url
            )
        except ValidationError as e:
            # Extract the error message
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', 'Validation error')
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"msg": error_msg}
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"msg": "Invalid input data"}
            )


class ResearchClubResponse(ResearchClubBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# RESEARCH PAPER
# =========================================================

class ResearchPaperBase(BaseModel):
    title: str
    slug: Optional[str] = None
    abstract: Optional[str] = None
    authors: Optional[str] = None
    published_date: Optional[datetime] = None
    paper_type: PaperType
    pdf_url: Optional[str] = None
    online_url: Optional[str] = None
    is_published: bool = True


class ResearchPaperCreate(ResearchPaperBase):
    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        abstract: Optional[str] = Form(None),
        authors: Optional[str] = Form(None),
        published_date: Optional[datetime] = Form(None),
        paper_type: PaperType = Form(...),
        online_url: Optional[str] = Form(None),
        is_published: bool = Form(True)
    ):
        try:
            return cls(
                title=title,
                abstract=abstract,
                authors=authors,
                published_date=published_date,
                paper_type=paper_type,
                online_url=online_url,
                is_published=is_published
            )
        except ValidationError as e:
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', 'Validation error')
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"msg": error_msg}
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"msg": "Invalid input data"}
            )


class ResearchPaperUpdate(BaseModel):
    """Schema for updating research papers - all fields optional"""
    title: Optional[str] = None
    slug: Optional[str] = None
    abstract: Optional[str] = None
    authors: Optional[str] = None
    published_date: Optional[datetime] = None
    paper_type: Optional[PaperType] = None
    pdf_url: Optional[str] = None
    online_url: Optional[str] = None
    is_published: Optional[bool] = None
    
    @classmethod
    def as_form(
        cls,
        title: Optional[str] = Form(None),
        abstract: Optional[str] = Form(None),
        authors: Optional[str] = Form(None),
        published_date: Optional[datetime] = Form(None),
        paper_type: Optional[PaperType] = Form(None),
        online_url: Optional[str] = Form(None),
        is_published: Optional[bool] = Form(None)
    ):
        try:
            return cls(
                title=title,
                abstract=abstract,
                authors=authors,
                published_date=published_date,
                paper_type=paper_type,
                online_url=online_url,
                is_published=is_published
            )
        except ValidationError as e:
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', 'Validation error')
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"msg": error_msg}
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"msg": "Invalid input data"}
            )


class ResearchPaperResponse(ResearchPaperBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# EVENT
# =========================================================

class EventBase(BaseModel):
    title: str
    slug: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    location: Optional[str] = None
    event_type: EventType
    is_active: bool = True


class EventCreate(EventBase):
    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: Optional[str] = Form(None),
        start_datetime: datetime = Form(...),
        end_datetime: Optional[datetime] = Form(None),
        location: Optional[str] = Form(None),
        event_type: EventType = Form(...),
        is_active: bool = Form(True)
    ):
        try:
            return cls(
                title=title,
                description=description,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                location=location,
                event_type=event_type,
                is_active=is_active
            )
        except ValidationError as e:
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', 'Validation error')
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"msg": error_msg}
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"msg": "Invalid input data"}
            )


class EventUpdate(BaseModel):
    """Schema for updating events - all fields optional"""
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    location: Optional[str] = None
    event_type: Optional[EventType] = None
    is_active: Optional[bool] = None
    
    @classmethod
    def as_form(
        cls,
        title: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        start_datetime: Optional[datetime] = Form(None),
        end_datetime: Optional[datetime] = Form(None),
        location: Optional[str] = Form(None),
        event_type: Optional[EventType] = Form(None),
        is_active: Optional[bool] = Form(None)
    ):
        try:
            return cls(
                title=title,
                description=description,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                location=location,
                event_type=event_type,
                is_active=is_active
            )
        except ValidationError as e:
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', 'Validation error')
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"msg": error_msg}
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"msg": "Invalid input data"}
            )


class EventResponse(EventBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# NEWS
# =========================================================

class NewsBase(BaseModel):
    title: str
    slug: Optional[str] = None
    summary: Optional[str] = None
    content: str
    image_url: Optional[str] = None
    is_published: bool = True


class NewsCreate(NewsBase):
    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        summary: Optional[str] = Form(None),
        content: str = Form(...),
        is_published: bool = Form(True)
    ):
        try:
            return cls(
                title=title,
                summary=summary,
                content=content,
                is_published=is_published
            )
        except ValidationError as e:
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', 'Validation error')
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"msg": error_msg}
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"msg": "Invalid input data"}
            )


class NewsUpdate(BaseModel):
    """Schema for updating news - all fields optional"""
    title: Optional[str] = None
    slug: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    is_published: Optional[bool] = None
    
    @classmethod
    def as_form(
        cls,
        title: Optional[str] = Form(None),
        summary: Optional[str] = Form(None),
        content: Optional[str] = Form(None),
        is_published: Optional[bool] = Form(None)
    ):
        try:
            return cls(
                title=title,
                summary=summary,
                content=content,
                is_published=is_published
            )
        except ValidationError as e:
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', 'Validation error')
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"msg": error_msg}
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"msg": "Invalid input data"}
            )


class NewsResponse(NewsBase):
    id: int
    published_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# ADVISORY BOARD
# =========================================================

class AdvisoryBoardMemberBase(BaseModel):
    name: str
    position: Optional[str] = None
    institution: Optional[str] = None
    expertise: Optional[str] = None
    bio: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True


class AdvisoryBoardMemberCreate(AdvisoryBoardMemberBase):
    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        position: Optional[str] = Form(None),
        institution: Optional[str] = Form(None),
        expertise: Optional[str] = Form(None),
        bio: Optional[str] = Form(None),
        is_active: bool = Form(True)
    ):
        try:
            return cls(
                name=name,
                position=position,
                institution=institution,
                expertise=expertise,
                bio=bio,
                is_active=is_active
            )
        except ValidationError as e:
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', 'Validation error')
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"msg": error_msg}
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"msg": "Invalid input data"}
            )


class AdvisoryBoardMemberUpdate(BaseModel):
    """Schema for updating advisory board members - all fields optional"""
    name: Optional[str] = None
    position: Optional[str] = None
    institution: Optional[str] = None
    expertise: Optional[str] = None
    bio: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    
    @classmethod
    def as_form(
        cls,
        name: Optional[str] = Form(None),
        position: Optional[str] = Form(None),
        institution: Optional[str] = Form(None),
        expertise: Optional[str] = Form(None),
        bio: Optional[str] = Form(None),
        is_active: Optional[bool] = Form(None)
    ):
        try:
            return cls(
                name=name,
                position=position,
                institution=institution,
                expertise=expertise,
                bio=bio,
                is_active=is_active
            )
        except ValidationError as e:
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', 'Validation error')
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={"msg": error_msg}
                )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"msg": "Invalid input data"}
            )

class AdvisoryBoardMemberResponse(AdvisoryBoardMemberBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)