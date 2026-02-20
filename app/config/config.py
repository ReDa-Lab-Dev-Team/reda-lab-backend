from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
from pydantic import Field
import os
from dotenv import load_dotenv



class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    
    # metadata uploads
    upload_dir: str = Field(default="uploads", env="UPLOAD_DIR")
    class Config:
        env_file = ".env"
        case_sensitive = False
        

settings = Settings()
