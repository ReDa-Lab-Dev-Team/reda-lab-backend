from pydantic import BaseModel, ConfigDict, EmailStr
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
    paused = "paused"


class EventType(str, Enum):
    workshop = "workshop"
    seminar = "seminar"
    conference = "conference"
    meeting = "meeting"


class PaperType(str, Enum):
    journal = "journal"
    conference = "conference"
    book = "book"
    report = "report"


# =========================================================
# CATEGORY
# =========================================================

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# TEAM MEMBER
# =========================================================

class TeamMemberBase(BaseModel):
    name: str
    position: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[EmailStr] = None
    photo_url: Optional[str] = None


class TeamMemberCreate(TeamMemberBase):
    is_active: bool = True


class TeamMemberResponse(TeamMemberBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# RESEARCH PROJECT
# =========================================================

class ResearchProjectBase(BaseModel):
    title: str
    slug: str
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


class ResearchProjectResponse(ResearchProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    contributors: List[TeamMemberResponse] = []
    categories: List[CategoryResponse] = []

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# PUBLICATION
# =========================================================

class PublicationBase(BaseModel):
    title: str
    slug: str
    abstract: Optional[str] = None
    journal: Optional[str] = None
    publication_date: Optional[datetime] = None
    paper_type: PaperType
    pdf_url: Optional[str] = None
    online_url: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    is_published: bool = True


class PublicationCreate(PublicationBase):
    author_ids: List[int] = []
    project_id: int


class PublicationResponse(PublicationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    authors: List[TeamMemberResponse] = []
    project_id: int

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# EVENT
# =========================================================

class EventBase(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    location: Optional[str] = None
    event_type: EventType
    is_active: bool = True


class EventCreate(EventBase):
    pass


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
    slug: str
    summary: Optional[str] = None
    content: str
    image_url: Optional[str] = None
    is_published: bool = True


class NewsCreate(NewsBase):
    pass


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


class AdvisoryBoardMemberResponse(AdvisoryBoardMemberBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
