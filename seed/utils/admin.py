from sqlalchemy.orm import Session
from typing import List
from app.utils.hash_pw import hash_pw
from app.utils.logging import log_message
from app.models.admin import Admin

@log_message
def create_user(db: Session, users: List):
    for user in users:
        hashed_password = hash_pw(str(user["password"]))
        user['hashed_password'] = hashed_password
        admin = Admin(
            email=user["email"],
            username=user["username"],
            hashed_password=hashed_password,
            is_active=user.get("is_active", True)
        )
        db.add(admin)
    db.commit()
    