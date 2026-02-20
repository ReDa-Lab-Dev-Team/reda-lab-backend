from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import login
from app.api.v1.admin import router as admin_router
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config.config import settings
import os
# from app.config.database import engine, Base

# Create all tables

## Now we use Alembic for migrations, so we don't need to create tables here. Alembic will handle it based on the models and migration scripts.
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="REDA Lab API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.upload_dir, exist_ok=True)

# Include routers
app.include_router(login.router)
app.include_router(prefix="/api/v1", router=admin_router)
# app.include_router(public.router)


app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

@app.get("/")
def read_root():
    return {"message": "Welcome to REDA Lab API"}