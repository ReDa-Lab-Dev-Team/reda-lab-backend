from sqlalchemy.orm import Session
from typing import List
from app.utils.logging import log_message
from app.models.admin import Admin

@log_message
def create_user(db: Session, users: List):
    for user in users:
        admin = Admin(
            email=user["email"],
            username=user["username"],
            role=user['role'],
            is_active=user.get("is_active", True)
        )
        admin.set_password(user["password"])
        db.add(admin)
    db.commit()
    