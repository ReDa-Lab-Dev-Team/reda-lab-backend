from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ProjectStatus(str, Enum):
    active = "active"
    completed = "completed"
    suspended = "suspended"

class EventType(str, Enum):
    conference = "conference"
    workshop = "workshop"
    seminar = "seminar"

class TeamMemberBase(BaseModel):
    name: str
    position: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[str] = None
    photo_url: Optional[str] = None

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMember(TeamMemberBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResearchProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: ProjectStatus = ProjectStatus.active
    funding_source: Optional[str] = None
    budget: Optional[int] = None

class ResearchProjectCreate(ResearchProjectBase):
    pass

class ResearchProject(ResearchProjectBase):
    id: int
    created_at: datetime
    contributors: List[TeamMember] = []
    
    class Config:
        from_attributes = True

class PublicationBase(BaseModel):
    title: str
    abstract: Optional[str] = None
    journal: Optional[str] = None
    publication_date: Optional[datetime] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    is_published: bool = True

class PublicationCreate(PublicationBase):
    pass

class Publication(PublicationBase):
    id: int
    created_at: datetime
    authors: List[TeamMember] = []
    project: Optional[ResearchProject] = None
    
    class Config:
        from_attributes = True

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    location: Optional[str] = None
    event_type: EventType

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class NewsBase(BaseModel):
    title: str
    content: str
    is_published: bool = True

class NewsCreate(NewsBase):
    pass

class News(NewsBase):
    id: int
    published_date: datetime
    author: Optional[TeamMember] = None
    
    class Config:
        from_attributes = True