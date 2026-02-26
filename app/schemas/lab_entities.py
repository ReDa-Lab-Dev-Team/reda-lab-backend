from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum
from decimal import Decimal


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
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        if v and not v.endswith('@gmail.com'):
            raise ValueError('Email must be from @gmail.com domain')
        return v


class TeamMemberCreate(TeamMemberBase):
    is_active: bool = True
    photo_url: Optional[str] = None


class TeamMemberUpdate(BaseModel):
    """Schema for updating team members - all fields optional"""
    name: Optional[str] = None
    position: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    photo_url: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email_domain(cls, v):
        if v and not v.endswith('@gmail.com'):
            raise ValueError('Email must be from @gmail.com domain')
        return v


class TeamMemberResponse(TeamMemberBase):
    id: int
    is_active: bool
    photo_url: Optional[str] = None

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
    pass


class ResearchClubUpdate(BaseModel):
    """Schema for updating research clubs - all fields optional"""
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    core_theme: Optional[str] = None
    leaders: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class ResearchClubResponse(ResearchClubBase):
    id: int
    created_at: datetime
    updated_at: datetime

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
    pass


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
    pass


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
    pass


class NewsUpdate(BaseModel):
    """Schema for updating news - all fields optional"""
    title: Optional[str] = None
    slug: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    is_published: Optional[bool] = None


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
    photo_url: Optional[str] = None
    is_active: bool = True


class AdvisoryBoardMemberCreate(AdvisoryBoardMemberBase):
    pass


class AdvisoryBoardMemberUpdate(BaseModel):
    """Schema for updating advisory board members - all fields optional"""
    name: Optional[str] = None
    position: Optional[str] = None
    institution: Optional[str] = None
    expertise: Optional[str] = None
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    is_active: Optional[bool] = None

class AdvisoryBoardMemberResponse(AdvisoryBoardMemberBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)