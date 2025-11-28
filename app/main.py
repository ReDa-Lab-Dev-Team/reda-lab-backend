from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, public, admin
from app.middleware.rate_limit import rate_limit_middleware
from app.config.database import create_tables

app = FastAPI(
    title="Lab Information System API",
    description="Backend API for lab information management system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Create tables on startup
@app.on_event("startup")
def on_startup():
    create_tables()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Include routers
app.include_router(auth.router)
app.include_router(public.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    return {"message": "Lab Information System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)