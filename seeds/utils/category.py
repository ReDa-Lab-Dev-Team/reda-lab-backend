from sqlalchemy.orm import Session
from typing import List
from app.utils.logging import log_message
from app.models.lab_entities import Category

@log_message
def create_category(db: Session, categories: List):
    for category in categories:
        cat = Category(
            name=category["name"],
            description=category["description"],
            created_by=category["created_by"]
        )
        db.add(cat)
    db.commit()