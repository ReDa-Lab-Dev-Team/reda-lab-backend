# ReDa Lab Backend

FastAPI-based backend for the ReDa Lab Information System (LIS). Provides API endpoints for authentication, administrative functions, and lab-related entities.

## Prerequisites

- **Python** `>= 3.11, < 3.13` (from `pyproject.toml`)
- **PostgreSQL** 15+
- **pip** (or **uv**)

## Project Layout (kheang branch)

```
reda-lab-backend/
├── app/                       # FastAPI application package
├── main.py                    # Entry point script
├── README.md
├── requirements.txt           # pip dependencies (if using pip)
├── pyproject.toml             # project + dependencies (uv / PEP 621)
├── uv.lock                    # uv lockfile
├── .env.example               # environment variables example
├── seed_data.py               # seed script
└── test_db_connection.py      # DB connection test script
```

## Quick Start

### 1) Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` if needed.

### 2) Install dependencies

Using pip:

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Or using uv:

```bash
uv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
uv sync
```

### 3) Run the backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Docs:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Useful Commands

### Seed Data

```bash
python seed_data.py
```

### Test DB Connection

```bash
python test_db_connection.py
```

## Support

For issues or questions, please contact the development team.
