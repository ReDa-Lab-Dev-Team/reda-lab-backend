from sqlalchemy.orm import Session
from app.models.admin import Admin

class UserService:
    def get_users(self, db: Session):
        return db.query(Admin).all()