from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base
from datetime import datetime

# Association tables for many-to-many relationships
project_contributors = Table(
    "project_contributors",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("research_projects.id")),
    Column("member_id", Integer, ForeignKey("team_members.id"))
)

publication_authors = Table(
    "publication_authors",
    Base.metadata,
    Column("publication_id", Integer, ForeignKey("publications.id")),
    Column("member_id", Integer, ForeignKey("team_members.id"))
)

class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    position = Column(String(100))
    bio = Column(Text)
    email = Column(String(100))
    photo_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    projects = relationship("ResearchProject", secondary=project_contributors, back_populates="contributors")
    publications = relationship("Publication", secondary=publication_authors, back_populates="authors")

class ResearchProject(Base):
    __tablename__ = "research_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(50), default="active")  # active, completed, suspended
    funding_source = Column(String(100))
    budget = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    contributors = relationship("TeamMember", secondary=project_contributors, back_populates="projects")
    publications = relationship("Publication", back_populates="project")

class Publication(Base):
    __tablename__ = "publications"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    abstract = Column(Text)
    journal = Column(String(200))
    publication_date = Column(DateTime)
    doi = Column(String(100))
    url = Column(String(255))
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    authors = relationship("TeamMember", secondary=publication_authors, back_populates="publications")
    project_id = Column(Integer, ForeignKey("research_projects.id"))
    project = relationship("ResearchProject", back_populates="publications")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime)
    location = Column(String(200))
    event_type = Column(String(50))  # conference, workshop, seminar
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class AdvisoryBoardMember(Base):
    __tablename__ = "advisory_board"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    position = Column(String(100))
    institution = Column(String(200))
    expertise = Column(String(200))
    bio = Column(Text)
    photo_url = Column(String(255))
    is_active = Column(Boolean, default=True)

class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    published_date = Column(DateTime, default=func.now())
    is_published = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationship
    author = relationship("User")