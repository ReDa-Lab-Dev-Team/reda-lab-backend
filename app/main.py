# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.api.v1 import login
# from app.api.v1.admin import router as admin_router
# from fastapi.staticfiles import StaticFiles
# from pathlib import Path
# from app.config.config import settings
# import os
# from app.middleware.auth import AuthMiddleware
# from starlette.middleware.trustedhost import TrustedHostMiddleware
# from app.middleware.rate_limit import rate_limit_middleware
# from app.middleware.security_headers import security_headers_middleware
# # from app.config.database import engine, Base

# # Create all tables

# ## Now we use Alembic for migrations, so we don't need to create tables here. Alembic will handle it based on the models and migration scripts.
# # Base.metadata.create_all(bind=engine)

# app = FastAPI(title="REDA Lab API")

# # Trusted Host middleware (prevents host header attacks)
# app.add_middleware(
#     TrustedHostMiddleware, 
#     allowed_hosts=["localhost", "127.0.0.1", "yourdomain.com"]
# )

# # CORS middleware - RESTRICT TO YOUR FRONTEND
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",  # Your frontend URL
#         "https://yourdomain.com"   # Production URL
#     ],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "PUT", "DELETE"],
#     allow_headers=["*"],
# )

# app.middleware("http")(security_headers_middleware)
# # Rate limiting middleware
# app.middleware("http")(rate_limit_middleware)

# # Authentication middleware
# app.add_middleware(AuthMiddleware)

# os.makedirs(settings.upload_dir, exist_ok=True)

# # Include routers
# app.include_router(login.router)
# app.include_router(prefix="/api/v1", router=admin_router)
# # app.include_router(public.router)


# app.mount("/upload", StaticFiles(directory=settings.upload_dir), name="upload")

# @app.get("/")
# def read_root():
#     return {"message": "Welcome to REDA Lab API"}



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from app.api.v1 import login
from app.api.v1.admin import router as admin_router
from fastapi.staticfiles import StaticFiles
from app.config.config import settings
import os
from app.middleware.auth import AuthMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from app.middleware.rate_limit import rate_limit_middleware
from app.middleware.security_headers import security_headers_middleware
from pathlib import Path

app = FastAPI(title="REDA Lab API")

# # 1. HTTPS Redirect (ONLY in production)
# if settings.ENVIRONMENT == "production":
#     app.add_middleware(HTTPSRedirectMiddleware)

# # 2. Trusted Host middleware
# if settings.ENVIRONMENT == "production":
#     app.add_middleware(
#         TrustedHostMiddleware, 
#         allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
#     )
# else:
#     app.add_middleware(
#         TrustedHostMiddleware, 
#         allowed_hosts=["localhost", "127.0.0.1", "testserver"]
#     )

# 3. GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)

# 4. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)

# 5. Security headers
app.middleware("http")(security_headers_middleware)

# 6. Rate limiting
app.middleware("http")(rate_limit_middleware)

# 7. Authentication (should be last)
app.add_middleware(AuthMiddleware)

os.makedirs(settings.upload_dir, exist_ok=True)

# Include routers
app.include_router(login.router)
app.include_router(prefix="/api/v1", router=admin_router)

app.mount("/upload", StaticFiles(directory=settings.upload_dir), name="upload")

@app.get("/", response_class=HTMLResponse)
def read_root():
    template_path = Path(__file__).parent / "templates" / "landing.html"
    with open(template_path, "r") as f:
        return f.read()