# Reda Lab Backend

A FastAPI-based backend for the Lab Information System. This API provides endpoints for managing lab entities, user authentication, and administrative functions.

## Prerequisites

Before running the backend, ensure you have the following installed:

- **Python 3.13+**
- **PostgreSQL 15+**
- **Docker & Docker Compose** (for containerized setup)
- **pip** (Python package manager)

## Project Structure

```
reda-backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config/
│   │   └── database.py         # Database configuration
│   ├── models/                 # SQLAlchemy database models
│   │   ├── user.py
│   │   └── lab_entities.py
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── user.py
│   │   └── lab_entities.py
│   ├── api/
│   │   └── v1/                 # API v1 endpoints
│   │       ├── auth.py         # Authentication endpoints
│   │       ├── public.py        # Public endpoints
│   │       └── admin.py         # Admin endpoints
│   ├── utils/
│   │   ├── auth.py            # Authentication utilities
│   │   └── security.py        # Security utilities
│   └── middleware/
│       └── rate_limit.py       # Rate limiting middleware
├── alembic/                    # Database migrations
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Quick Start

### Option 1: Using Docker Compose (Recommended)

The simplest way to run the entire project with all dependencies:

```bash
cd ..  # Navigate to project root
docker-compose up -d
```

This command will:

- Start PostgreSQL database on port 5432
- Start PgAdmin on port 5050
- Start the FastAPI backend on port 8000

**Access the services:**

- API Documentation: http://localhost:8000/docs
- ReDoc Documentation: http://localhost:8000/redoc
- PgAdmin: http://localhost:5050
  - Email: `admin@lab.com`
  - Password: `admin123`

### Option 2: Local Development Setup

#### 1. Install Dependencies

```bash
# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

#### 2. Set Up Database

Ensure PostgreSQL is running on your machine. Create the database and user if needed:

```sql
CREATE USER lab_user WITH PASSWORD 'lab_pass';
CREATE DATABASE lab_db OWNER lab_user;
```

Or use Docker for PostgreSQL only:

```bash
docker run -d \
  --name lab_db \
  -e POSTGRES_DB=lab_db \
  -e POSTGRES_USER=lab_user \
  -e POSTGRES_PASSWORD=lab_pass \
  -p 5432:5432 \
  postgres:15
```

#### 3. Configure Environment Variables

Create a `.env` file in the `reda-backend` directory:

```env
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql://lab_user:lab_pass@localhost:5432/lab_db
```

#### 4. Run the Backend Server

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Swagger UI (Interactive):** http://localhost:8000/docs
- **ReDoc (Alternative UI):** http://localhost:8000/redoc

## Useful Commands

### Database Migrations (Alembic)

```bash
# Create a new migration
alembic revision --autogenerate -m "description of change"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Seed Data

```bash
python seed_data.py
```

### Run Tests (if available)

```bash
pytest
```

## Environment Variables

Key environment variables that can be configured:

| Variable                      | Default                                                | Description                      |
| ----------------------------- | ------------------------------------------------------ | -------------------------------- |
| `SECRET_KEY`                  | `your-super-secret-key-change-in-production`           | JWT secret key for token signing |
| `ALGORITHM`                   | `HS256`                                                | JWT algorithm                    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                                                   | JWT token expiration time        |
| `DATABASE_URL`                | `postgresql://lab_user:lab_pass@localhost:5432/lab_db` | PostgreSQL connection string     |

## Dependencies

Key Python packages used:

- **FastAPI** - Modern web framework for building APIs
- **Uvicorn** - ASGI server
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation and settings management
- **Alembic** - Database migrations
- **psycopg2-binary** - PostgreSQL adapter
- **python-jose** - JWT token handling
- **passlib + bcrypt** - Password hashing and verification
- **redis** - Caching layer

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
# Use a different port
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Database Connection Error

Verify the database is running and the connection string is correct:

```bash
# Test PostgreSQL connection
psql -U lab_user -d lab_db -h localhost
```

### Module Not Found Error

Ensure you're in the project directory and have activated the virtual environment:

```bash
cd reda-backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Docker Container Issues

Stop and remove containers, then restart:

```bash
docker-compose down
docker-compose up -d
```

## Development Best Practices

1. **Use Virtual Environment:** Always use a Python virtual environment to avoid dependency conflicts
2. **Environment Variables:** Never commit sensitive data; use `.env` files
3. **Database Migrations:** Create migrations for schema changes using Alembic
4. **API Documentation:** Keep docstrings updated for auto-generated API docs
5. **Security:** Change default secret keys and credentials in production

## Production Deployment

For production deployment:

1. Set `SECRET_KEY` to a strong, random value
2. Set `DATABASE_URL` to production database
3. Disable CORS `allow_origins=["*"]` and specify allowed domains
4. Use environment-specific configuration
5. Enable HTTPS
6. Set up proper logging and monitoring

## Support

For issues or questions, please refer to the main project README or contact the development team.
