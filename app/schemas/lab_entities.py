from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional
from datetime import datetime, date
from enum import Enum

# -----------------------------------------------------------------------------
# ENUMS (Match your database values)
# -----------------------------------------------------------------------------

class ProjectStatus(str, Enum):
    active = "active"
    completed = "completed"
    suspended = "suspended"
    on_going = "On going"  # For Figma
    done = "Done"          # For Figma

class EventType(str, Enum):
    conference = "conference"
    workshop = "workshop"
    seminar = "seminar"
    bootcamp = "bootcamp"

class PaperType(str, Enum):
    journal = "Journal"
    workshop = "Workshop"
    conference = "Conference"
    thesis = "Thesis"

# -----------------------------------------------------------------------------
# CATEGORY SCHEMAS (NEW - for project filters)
# -----------------------------------------------------------------------------

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------------------------------------------
# TEAM MEMBER SCHEMAS
# -----------------------------------------------------------------------------

class TeamMemberBase(BaseModel):
    name: str
    position: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[str] = None
    photo_url: Optional[str] = None

class TeamMemberCreate(TeamMemberBase):
    is_active: bool = True

class TeamMemberResponse(TeamMemberBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------------------------------------------
# RESEARCH PROJECT SCHEMAS (UPDATED)
# -----------------------------------------------------------------------------

class ResearchProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None      # NEW for Figma
    is_featured: bool = False            # NEW for Figma
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = "On going"             # Changed for Figma
    funding_source: Optional[str] = None
    budget: Optional[int] = None

class ResearchProjectCreate(ResearchProjectBase):
    contributor_ids: List[int] = []      # For many-to-many
    category_ids: List[int] = []         # NEW for filters

class ResearchProjectResponse(ResearchProjectBase):
    id: int
    created_at: datetime
    contributors: List[TeamMemberResponse] = []
    categories: List[CategoryResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------------------------------------------
# PUBLICATION SCHEMAS (UPDATED)
# -----------------------------------------------------------------------------

class PublicationBase(BaseModel):
    title: str
    abstract: Optional[str] = None
    journal: Optional[str] = None
    publication_date: Optional[datetime] = None
    paper_type: str = "Journal"          # NEW for Figma badges
    pdf_url: Optional[str] = None        # NEW for Download button
    online_url: Optional[str] = None     # NEW for View Online button
    doi: Optional[str] = None
    url: Optional[str] = None
    is_published: bool = True

class PublicationCreate(PublicationBase):
    author_ids: List[int] = []           # For many-to-many
    project_id: Optional[int] = None

class PublicationResponse(PublicationBase):
    id: int
    created_at: datetime
    authors: List[TeamMemberResponse] = []
    project_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------------------------------------------
# EVENT SCHEMAS (UPDATED)
# -----------------------------------------------------------------------------

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None      # NEW for Figma
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    location: Optional[str] = None
    event_type: str = "workshop"
    is_active: bool = True

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------------------------------------------
# NEWS SCHEMAS (UPDATED)
# -----------------------------------------------------------------------------

class NewsBase(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None      # NEW for Figma
    is_published: bool = True

class NewsCreate(NewsBase):
    created_by: Optional[int] = None     # User ID (admin)

class NewsResponse(NewsBase):
    id: int
    published_date: datetime
    created_by: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------------------------------------------
# ADVISORY BOARD SCHEMAS
# -----------------------------------------------------------------------------

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
    
    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------------------------------------------
# ALIASES FOR BACKWARD COMPATIBILITY
# -----------------------------------------------------------------------------

ResearchProject = ResearchProjectResponse
Publication = PublicationResponse
Event = EventResponse
News = NewsResponse
TeamMember = TeamMemberResponse
AdvisoryBoardMember = AdvisoryBoardMemberResponse
Category = CategoryResponse