from .admin import AdminCreate, AdminResponse, AdminLogin, Token, User, UserCreate, UserResponse, UserLogin
from .lab_entities import (
    # Categories
    CategoryCreate, CategoryResponse,
    # Projects
    ResearchProjectCreate, ResearchProjectResponse,
    # Publications
    PublicationCreate, PublicationResponse,
    # Events
    EventCreate, EventResponse,
    # News
    NewsCreate, NewsResponse,
    # Team
    TeamMemberCreate, TeamMemberResponse,
    # Advisory
    AdvisoryBoardMemberCreate, AdvisoryBoardMemberResponse
)

__all__ = [
    # Admin schemas (new names)
    "AdminCreate", "AdminResponse", "AdminLogin", "Token",
    # Backward compatibility aliases
    "User", "UserCreate", "UserResponse", "UserLogin",
    # Lab entities
    "CategoryCreate", "CategoryResponse",
    "ResearchProjectCreate", "ResearchProjectResponse",
    "PublicationCreate", "PublicationResponse",
    "EventCreate", "EventResponse",
    "NewsCreate", "NewsResponse",
    "TeamMemberCreate", "TeamMemberResponse",
    "AdvisoryBoardMemberCreate", "AdvisoryBoardMemberResponse"
]