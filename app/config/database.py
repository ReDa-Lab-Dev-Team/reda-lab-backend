from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
from pydantic import Field
import os
from dotenv import load_dotenv

# Load .env file from project root
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(env_path)
print(f"Loaded environment variables from: {env_path}")

# Settings for the application
class Settings(BaseSettings):
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    database_url: str = Field(
        default="postgresql://lab_user:lab_pass@localhost:5432/lab_db",
        alias="DATABASE_URL"
    )
    environment: str = Field(default="development")
    debug: bool = Field(default=True)

    class Config:
        env_file = ".env"
        case_sensitive = False
        

settings = Settings()

# Database setup
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections after 5 minutes
    echo=settings.debug
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    # Import models here to register them with Base
    from app.models.user import User
    from app.models.lab_entities import (
        TeamMember, ResearchProject, Publication, 
        Event, AdvisoryBoardMember, News
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")