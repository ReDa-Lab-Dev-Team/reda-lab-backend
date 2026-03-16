from sqlalchemy.orm import Session
from typing import List
from app.utils.logging import log_message
from app.models.lab_entities import AdvisoryBoardMember

@log_message
def create_advisory_board_members(db: Session, members: List):
    for member in members:
        adv_member = AdvisoryBoardMember(
            name=member["name"],
            position=member["position"],
            institution=member["institution"],
            expertise=member["expertise"],
            bio=member["bio"],
            is_active=member["is_active"],
            created_by=member["created_by"]
        )
        db.add(adv_member)
    db.commit()