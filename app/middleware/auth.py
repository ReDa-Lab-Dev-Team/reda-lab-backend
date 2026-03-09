from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import Request
from app.utils.oauth2 import verify_access_token
from app.models.admin import Admin
from app.config.database import SessionLocal

# This middleware checks for a valid JWT token in the Authorization header for protected routes.

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        public_routes = [
            '/',
            '/login', # public routes
            '/docs',
            '/redoc',
            '/openapi.json',
        ]
        
        # Allow access to entire upload folder
        if request.url.path in public_routes or request.url.path.startswith('/upload/'):
            return await call_next(request)# Skip auth check

        # print(f"Incoming request: {request.method} {request.url.path}")

        
        # 2. Extract token from header
        auth_header = request.headers.get("Authorization")
        # print(f"Authorization header: {auth_header}")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized: No valid token provided"},
            )

        token = auth_header.split("Bearer ")[1]
        # print(f"Extracted token: {token}")

        # Verify token
        token_data = verify_access_token(token) # get id
        # print(f"Token data: {token_data}")
        

        if not token_data:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
            )

        # Fetch user from DB
        db = SessionLocal()
        try:
            user = db.query(Admin).filter(Admin.id == token_data.id).first()

            if not user:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "User not found"},
                )

            # Store in request.state
            request.state.user = user

        finally:
            db.close()

        return await call_next(request)