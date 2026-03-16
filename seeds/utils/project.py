from sqlalchemy.orm import Session
from typing import List
from app.utils.logging import log_message
from app.models.lab_entities import ResearchProject
from app.utils.helper_functions import slugify

@log_message
def create_research_project(db: Session, projects: List):
    for project in projects:
        # Auto-generate slug from title if not provided
        slug = project.get("slug") or slugify(project["title"])
        
        proj = ResearchProject(
            title=project["title"],
            slug=slug,
            description=project.get("description"),
            image_url=project.get("image_url"),
            is_featured=project.get("is_featured", False),
            start_date=project.get("start_date"),
            end_date=project.get("end_date"),
            status=project["status"],
            funding_source=project.get("funding_source"),
            budget=project.get("budget"),
            created_by=project["created_by"]
        )
        db.add(proj)
    db.commit()