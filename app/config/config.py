from pydantic_settings import BaseSettings
from pydantic import Field



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
    upload_dir: str = Field(default="upload", env="UPLOAD_DIR") # find dir name in env , if not found use "upload" as default
    class Config:
        env_file = ".env"
        case_sensitive = False
        

settings = Settings()
# ENVIRONMENT=development  # Change to "production" when deploying
