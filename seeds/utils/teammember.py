from sqlalchemy.orm import Session
from typing import List
from app.utils.logging import log_message
from app.models.lab_entities import TeamMember

@log_message
def create_teammember(db: Session, teammembers: List):
    for member in teammembers:
        tm = TeamMember(
            name=member["name"],
            position=member["position"],
            bio=member["bio"],
            email=member["email"],
            image_url=member["image_url"],
            is_active=member["is_active"],
            created_by=member["created_by"]
        )
        db.add(tm)
    db.commit()
    