from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

"""
format: 
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost/db_name"

"""

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#request database session dependency , when it done it will close the session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()