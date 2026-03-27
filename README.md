# ReDa Lab Backend

FastAPI-based backend for the ReDa Lab Information System (LIS). Provides API endpoints for authentication, administrative functions, and lab-related entities.

## Tech Stack

- FastAPI + Uvicorn
- PostgreSQL
- SQLAlchemy + Alembic
- Pydantic
- JWT Auth
- Docker / Docker Compose

## Prerequisites

- **Python 3.13+**
- **PostgreSQL 15+**
- **pip**
- (Optional) **Docker & Docker Compose** for containerized setup
- (Optional) **uv** (Astral) for dependency management

## Project Structure

```
reda-lab-backend/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── config/
│   │   └── database.py         # Database configuration
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   └── lab_entities.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   └── lab_entities.py
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py         # Authentication endpoints
│   │       ├── public.py       # Public endpoints
│   │       └── admin.py        # Admin endpoints
│   ├── utils/
│   │   ├── auth.py             # Auth utilities
│   │   └── security.py         # Security utilities
│   └── middleware/
│       └── rate_limit.py       # Rate limiting middleware
├── alembic/                    # Database migrations
├── requirements.txt            # Python dependencies
└── README.md
```

## Quick Start

### Option 1: Docker Compose (recommended)

From the repository root (same folder as `docker-compose.yml`), run:

```bash
docker-compose up -d
```

This typically starts:

- PostgreSQL on `localhost:5432`
- PgAdmin on `localhost:5050`
- FastAPI on `localhost:8000`

Access:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- PgAdmin: `http://localhost:5050`
  - Email: `admin@lab.com`
  - Password: `admin123`

### Option 2: Local development (without Docker)

#### 1) Create & activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

#### 2) Install dependencies

Using pip:

```bash
pip install -r requirements.txt
```

Or using `uv`:

```bash
# Example (adjust Python version as needed)
uv python install 3.12
uv venv --python 3.12
source venv/bin/activate  # or venv\Scripts\activate on Windows
uv sync
```

#### 3) Set up PostgreSQL

Create a database and user (example):

```sql
CREATE USER lab_user WITH PASSWORD 'lab_pass';
CREATE DATABASE lab_db OWNER lab_user;
```

Or run PostgreSQL via Docker only:

```bash
docker run -d \
  --name lab_db \
  -e POSTGRES_DB=lab_db \
  -e POSTGRES_USER=lab_user \
  -e POSTGRES_PASSWORD=lab_pass \
  -p 5432:5432 \
  postgres:15
```

#### 4) Configure environment variables

Create a `.env` file (adjust values as needed):

```env
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=postgresql://lab_user:lab_pass@localhost:5432/lab_db
```

#### 5) Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at `http://localhost:8000`.

## Database Migrations (Alembic)

```bash
# Create a new migration
alembic revision --autogenerate -m "describe change"

# Apply migrations
alembic upgrade head

# Roll back one migration
alembic downgrade -1
```

## Seed Data

```bash
python seed_data.py
```

## Running Tests

```bash
pytest
```

## Environment Variables

| Variable                      | Example / Default                                        | Description                      |
|------------------------------|----------------------------------------------------------|----------------------------------|
| `SECRET_KEY`                  | `your-super-secret-key-change-in-production`             | JWT secret key for token signing |
| `ALGORITHM`                   | `HS256`                                                  | JWT algorithm                    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                                                     | JWT token expiration time        |
| `DATABASE_URL`                | `postgresql://lab_user:lab_pass@localhost:5432/lab_db`   | PostgreSQL connection string     |

## Troubleshooting

### Port already in use

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Database connection error

Confirm Postgres is running and your `DATABASE_URL` is correct:

```bash
psql -U lab_user -d lab_db -h localhost
```

### Module not found / import errors

Make sure you are in the repo root and your venv is activated:

```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Docker containers issues

```bash
docker-compose down
docker-compose up -d
```

## Production Notes

At minimum before deploying:

1. Set `SECRET_KEY` to a strong random value
2. Use a production `DATABASE_URL`
3. Restrict CORS (avoid `allow_origins=["*"]` in production)
4. Use HTTPS
5. Add logging/monitoring

## Support

For questions/issues, contact the ReDa Lab development team or open an issue in this repository.
