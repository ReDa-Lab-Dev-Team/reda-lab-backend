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
    upcoming = "upcoming"
    paused = "paused"


class EventType(enum.Enum):
    workshop = "workshop"
    seminar = "seminar"
    conference = "conference"
    meeting = "meeting"


class PaperType(enum.Enum):
    journal = "journal"              # Journal article
    conference = "conference"        # Conference paper/proceedings
    workshop = "workshop"            # Workshop paper (as shown in your Figma)
    book_chapter = "book_chapter"    # Book chapter
    thesis = "thesis"                # PhD/Master's thesis
    technical_report = "technical_report"  # Technical report
    preprint = "preprint"            # arXiv, bioRxiv, etc.
    poster = "poster"                # Conference poster


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

# research_paper_authors = Table(
#     "research_paper_authors",
#     Base.metadata,
#     Column(
#         "paper_id",
#         Integer,
#         ForeignKey("research_papers.id", ondelete="CASCADE"),
#         primary_key=True,
#     ),
#     Column(
#         "member_id",
#         Integer,
#         ForeignKey("team_members.id", ondelete="CASCADE"),
#         primary_key=True,
#     ),
# )

# research_club_leaders = Table(
#     "research_club_leaders",
#     Base.metadata,
#     Column(
#         "club_id",
#         Integer,
#         ForeignKey("research_clubs.id", ondelete="CASCADE"),
#         primary_key=True,
#     ),
#     Column(
#         "member_id",
#         Integer,
#         ForeignKey("team_members.id", ondelete="CASCADE"),
#         primary_key=True,
#     ),
# )

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
    
    categories = relationship(
        "Category",
        secondary=project_categories,
        back_populates="projects",
    )
    
    # def __repr__(self):
    #     return f"<ResearchProject(id={self.id}, title='{self.title}', status='{self.status.value}')>"


# =========================================================
# RESEARCH CLUB
# =========================================================

class ResearchClub(Base, TimestampMixin):
    __tablename__ = "research_clubs"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(200), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)

    description = Column(Text)
    core_theme = Column(String(300))
    leaders = Column(String(500))
    image_url = Column(String(255))

    is_active = Column(Boolean, default=True, index=True)

    created_by = Column(
        Integer,
        ForeignKey("admins.id", ondelete="CASCADE"),
        nullable=False,
    )


# =========================================================
# RESEARCH PAPER
# =========================================================

# class ResearchPaper(Base, TimestampMixin):
#     __tablename__ = "research_papers"

#     id = Column(Integer, primary_key=True, index=True)

#     title = Column(String(300), nullable=False)
#     slug = Column(String(255), unique=True, nullable=False, index=True)

#     title = Column(Text)
#     description = Column(Text)

#     published_date = Column(DateTime, index=True)

#     paper_type = Column(
#         Enum(PaperType),
#         nullable=False,
#         index=True,
#     )

#     pdf_url = Column(String(255))
#     online_url = Column(String(255))
#     url = Column(String(255))

#     is_published = Column(Boolean, default=True, index=True)

#     club_id = Column(
#         Integer,
#         ForeignKey("research_clubs.id", ondelete="CASCADE"),
#         nullable=True,
#     )

#     project_id = Column(
#         Integer,
#         ForeignKey("research_projects.id", ondelete="CASCADE"),
#         nullable=True,
#     )

#     created_by = Column(
#         Integer,
#         ForeignKey("admins.id", ondelete="CASCADE"),
#         nullable=False,
#     )

#     club = relationship("ResearchClub", back_populates="research_papers")
#     project = relationship("ResearchProject", back_populates="research_papers")

#     authors = relationship(
#         "TeamMember",
#         secondary=research_paper_authors,
#         back_populates="research_papers",
#     )

class ResearchPaper(Base, TimestampMixin):
    __tablename__ = "research_papers"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(300), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)

    abstract = Column(Text)
    authors = Column(String(500))  # Simple text field for author names

    published_date = Column(DateTime, index=True)

    paper_type = Column(
        Enum(PaperType),
        nullable=False,
        index=True,
    )

    pdf_url = Column(String(255))
    online_url = Column(String(255))

    is_published = Column(Boolean, default=True, index=True)

    created_by = Column(
        Integer,
        ForeignKey("admins.id", ondelete="CASCADE"),
        nullable=False,
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
    image_url = Column(String(255))

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

    # research_papers = relationship(
    #     "ResearchPaper",
    #     secondary=research_paper_authors,
    #     back_populates="authors",
    # )

    # led_clubs = relationship(
    #     "ResearchClub",
    #     secondary=research_club_leaders,
    #     back_populates="leaders",
    # )

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

    image_url = Column(String(255))

    is_active = Column(Boolean, default=True, index=True)

    created_by = Column(
        Integer,
        ForeignKey("admins.id", ondelete="CASCADE"),
        nullable=False,
    )
