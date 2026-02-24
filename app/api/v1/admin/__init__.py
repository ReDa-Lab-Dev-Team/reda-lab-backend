from fastapi import APIRouter
from .projects import router as projects_router
from .events import router as events_router
from .team_members import router as team_members_router
from .news import router as news_router
from .advisory_board import router as advisory_board_router
from .categories import router as categories_router
from .users import public_router as user_public_router, protected_router as user_protected_router

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

# Include all sub-routers
router.include_router(projects_router)
router.include_router(events_router)
router.include_router(team_members_router)
router.include_router(news_router)
router.include_router(advisory_board_router)
router.include_router(categories_router)
router.include_router(user_public_router)
router.include_router(user_protected_router)