from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
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

# --- NEW: Category Table (MISSING from your schema but needed for filters) ---

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # "LLM", "CV Club", "Fintech"
    projects = relationship("ResearchProject", secondary=project_categories, back_populates="categories")

# --- UPDATED: ResearchProject (Add Figma fields) ---

class ResearchProject(Base):
    __tablename__ = "research_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # ADD THESE for Figma
    image_url = Column(String(255))  # Project card images
    is_featured = Column(Boolean, default=False)  # Home page featured section
    
    # Keep your detailed fields
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(50), default="active")  # Change to "On going", "Done" for Figma
    funding_source = Column(String(100))
    budget = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    
    contributors = relationship("TeamMember", secondary=project_contributors, back_populates="projects")
    publications = relationship("Publication", back_populates="project")
    categories = relationship("Category", secondary=project_categories, back_populates="projects")

# --- UPDATED: Publication (Add Figma fields) ---

class Publication(Base):
    __tablename__ = "publications"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    abstract = Column(Text)
    journal = Column(String(200))
    publication_date = Column(DateTime)
    
    # ADD THESE for Figma
    paper_type = Column(String(50))  # "Journal", "Workshop", "Thesis", "Conference"
    pdf_url = Column(String(255))  # "Download PDF" button
    online_url = Column(String(255))  # "View Online" button
    
    # Keep your fields
    doi = Column(String(100))
    url = Column(String(255))  # Keep as backup
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    authors = relationship("TeamMember", secondary=publication_authors, back_populates="publications")
    project_id = Column(Integer, ForeignKey("research_projects.id"))
    project = relationship("ResearchProject", back_populates="publications")

# --- UPDATED: Event (Add image) ---

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # ADD THIS for Figma
    image_url = Column(String(255))  # Event card images
    
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime)
    location = Column(String(200))
    event_type = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

# --- UPDATED: News (Add image) ---

class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # ADD THIS for Figma
    image_url = Column(String(255))  # News card images
    
    published_date = Column(DateTime, default=func.now())
    is_published = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    author = relationship("User")

# --- Keep Your TeamMember (It's good!) ---

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
    
    projects = relationship("ResearchProject", secondary=project_contributors, back_populates="contributors")
    publications = relationship("Publication", secondary=publication_authors, back_populates="authors")

# --- Keep AdvisoryBoardMember (Might be useful) ---

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