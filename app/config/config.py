from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field



class Settings(BaseSettings):
    # Database settings
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    
    # Auth settings
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    
    # File uploads
    upload_dir: str = Field(default="upload", validation_alias="UPLOAD_DIR")
    
    # Pydantic v2 config
    model_config = SettingsConfigDict(
        # env_file=".env",
        case_sensitive=False,
        extra="ignore",  # Ignore undefined env vars
        env_prefix=""    # No prefix required
    )

settings = Settings()
# ENVIRONMENT=development  # Change to "production" when deploying
