from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth
from app.api.v1.admin import router as admin_router
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

# Include routers
app.include_router(auth.router)
app.include_router(admin_router, prefix="/api/v1")
# app.include_router(public.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to REDA Lab API"}