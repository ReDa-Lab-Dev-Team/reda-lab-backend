from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text, TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base

# --- Association Tables ---

project_contributors = Table(
    "project_contributors", Base.metadata,
    Column("project_id", Integer, ForeignKey("research_projects.id"), primary_key=True),
    Column("member_id", Integer, ForeignKey("team_members.id"), primary_key=True)
)

publication_authors = Table(
    "publication_authors", Base.metadata,
    Column("publication_id", Integer, ForeignKey("publications.id"), primary_key=True),
    Column("member_id", Integer, ForeignKey("team_members.id"), primary_key=True)
)

project_categories = Table(
    'project_categories', Base.metadata,
    Column('project_id', Integer, ForeignKey('research_projects.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

# --- Category Table ---

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False) 
    
    projects = relationship("ResearchProject", secondary=project_categories, back_populates="categories")

class ResearchProject(Base):
    __tablename__ = "research_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    image_url = Column(String(255))
    is_featured = Column(Boolean, default=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(50), default="active")
    funding_source = Column(String(100))
    budget = Column(Integer)
    created_by = Column(Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False) 
    
    contributors = relationship("TeamMember", secondary=project_contributors, back_populates="projects")
    publications = relationship("Publication", back_populates="project")
    categories = relationship("Category", secondary=project_categories, back_populates="projects")

# --- Publication ---

class Publication(Base):
    __tablename__ = "publications"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    abstract = Column(Text)
    journal = Column(String(200))
    publication_date = Column(DateTime)
    paper_type = Column(String(50))
    pdf_url = Column(String(255))
    online_url = Column(String(255))
    doi = Column(String(100))
    url = Column(String(255))
    is_published = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False)
    
    authors = relationship("TeamMember", secondary=publication_authors, back_populates="publications")
    project_id = Column(Integer, ForeignKey("research_projects.id"))
    project = relationship("ResearchProject", back_populates="publications")

# --- Event ---

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    image_url = Column(String(255))
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime)
    location = Column(String(200))
    event_type = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False) 

# --- News ---

class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    summary = Column(Text)
    content = Column(Text, nullable=False)
    image_url = Column(String(255))
    published_date = Column(DateTime, default=func.now())
    is_published = Column(Boolean, default=True)
    # Removed created_by and author - only 1 admin

# --- TeamMember ---

class TeamMember(Base):
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    position = Column(String(100))
    bio = Column(Text)
    email = Column(String(100))
    photo_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False) 
    
    projects = relationship("ResearchProject", secondary=project_contributors, back_populates="contributors")
    publications = relationship("Publication", secondary=publication_authors, back_populates="authors")

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
    created_by = Column(Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False)