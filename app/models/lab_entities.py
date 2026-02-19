from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    ForeignKey, Table, Text, TIMESTAMP,
    Enum, Numeric
)
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.config.database import Base
import enum


# =========================================================
# ENUMS
# =========================================================

class ProjectStatus(enum.Enum):
    active = "active"
    completed = "completed"
    paused = "paused"


class EventType(enum.Enum):
    workshop = "workshop"
    seminar = "seminar"
    conference = "conference"
    meeting = "meeting"


class PaperType(enum.Enum):
    journal = "journal"
    conference = "conference"
    book = "book"
    report = "report"


# =========================================================
# ASSOCIATION TABLES (Many-to-Many)
# =========================================================

project_contributors = Table(
    "project_contributors",
    Base.metadata,
    Column(
        "project_id",
        Integer,
        ForeignKey("research_projects.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "member_id",
        Integer,
        ForeignKey("team_members.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

publication_authors = Table(
    "publication_authors",
    Base.metadata,
    Column(
        "publication_id",
        Integer,
        ForeignKey("publications.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "member_id",
        Integer,
        ForeignKey("team_members.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

project_categories = Table(
    "project_categories",
    Base.metadata,
    Column(
        "project_id",
        Integer,
        ForeignKey("research_projects.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "category_id",
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# =========================================================
# BASE MIXIN (Soft Delete + Audit)
# =========================================================

class TimestampMixin:
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        index=True,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=func.now(),
        index=True,
    )
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)


# =========================================================
# CATEGORY
# =========================================================

class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)

    created_by = Column(
        Integer,
        ForeignKey("admins.id", ondelete="CASCADE"),
        nullable=False,
    )

    projects = relationship(
        "ResearchProject",
        secondary=project_categories,
        back_populates="categories",
    )


# =========================================================
# RESEARCH PROJECT
# =========================================================

class ResearchProject(Base, TimestampMixin):
    __tablename__ = "research_projects"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)

    description = Column(Text)
    image_url = Column(String(255))

    is_featured = Column(Boolean, default=False, index=True)

    start_date = Column(DateTime)
    end_date = Column(DateTime)

    status = Column(
        Enum(ProjectStatus),
        default=ProjectStatus.active,
        nullable=False,
        index=True,
    )

    funding_source = Column(String(100))

    budget = Column(Numeric(15, 2))  # Money-safe type

    created_by = Column(
        Integer,
        ForeignKey("admins.id", ondelete="CASCADE"),
        nullable=False,
    )

    contributors = relationship(
        "TeamMember",
        secondary=project_contributors,
        back_populates="projects",
    )

    publications = relationship(
        "Publication",
        back_populates="project",
        cascade="all, delete",
    )

    categories = relationship(
        "Category",
        secondary=project_categories,
        back_populates="projects",
    )


# =========================================================
# PUBLICATION
# =========================================================

class Publication(Base, TimestampMixin):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(300), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)

    abstract = Column(Text)
    journal = Column(String(200))

    publication_date = Column(DateTime, index=True)

    paper_type = Column(
        Enum(PaperType),
        nullable=False,
        index=True,
    )

    pdf_url = Column(String(255))
    online_url = Column(String(255))
    doi = Column(String(100))
    url = Column(String(255))

    is_published = Column(Boolean, default=True, index=True)

    project_id = Column(
        Integer,
        ForeignKey("research_projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_by = Column(
        Integer,
        ForeignKey("admins.id", ondelete="CASCADE"),
        nullable=False,
    )

    project = relationship("ResearchProject", back_populates="publications")

    authors = relationship(
        "TeamMember",
        secondary=publication_authors,
        back_populates="publications",
    )


# =========================================================
# EVENT
# =========================================================

class Event(Base, TimestampMixin):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)

    description = Column(Text)
    image_url = Column(String(255))

    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime)

    location = Column(String(200))

    event_type = Column(
        Enum(EventType),
        nullable=False,
        index=True,
    )

    is_active = Column(Boolean, default=True, index=True)

    created_by = Column(
        Integer,
        ForeignKey("admins.id", ondelete="CASCADE"),
        nullable=False,
    )


# =========================================================
# NEWS
# =========================================================

class News(Base, TimestampMixin):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)

    summary = Column(Text)
    content = Column(Text, nullable=False)

    image_url = Column(String(255))

    published_date = Column(DateTime, default=func.now(), index=True)

    is_published = Column(Boolean, default=True, index=True)

    created_by = Column(
        Integer,
        ForeignKey("admins.id", ondelete="CASCADE"),
        nullable=False,
    )


# =========================================================
# TEAM MEMBER
# =========================================================

class TeamMember(Base, TimestampMixin):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False, index=True)
    position = Column(String(100))
    bio = Column(Text)

    email = Column(String(100), unique=True)
    photo_url = Column(String(255))

    is_active = Column(Boolean, default=True, index=True)

    created_by = Column(
        Integer,
        ForeignKey("admins.id", ondelete="CASCADE"),
        nullable=False,
    )

    projects = relationship(
        "ResearchProject",
        secondary=project_contributors,
        back_populates="contributors",
    )

    publications = relationship(
        "Publication",
        secondary=publication_authors,
        back_populates="authors",
    )


# =========================================================
# ADVISORY BOARD
# =========================================================

class AdvisoryBoardMember(Base, TimestampMixin):
    __tablename__ = "advisory_board"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    position = Column(String(100))
    institution = Column(String(200))
    expertise = Column(String(200))
    bio = Column(Text)

    photo_url = Column(String(255))

    is_active = Column(Boolean, default=True, index=True)

    created_by = Column(
        Integer,
        ForeignKey("admins.id", ondelete="CASCADE"),
        nullable=False,
    )
