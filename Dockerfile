# Stage 1: Build stage
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.17 /uv /bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies into a virtual environment
RUN uv venv /app/.venv && \
    UV_PROJECT_ENVIRONMENT=/app/.venv uv sync --frozen

# Stage 2: Runtime stage
FROM python:3.12-slim AS runtime

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.17 /uv /bin/uv

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY . .

# Set ownership
RUN chown -R appuser:appuser /app

USER appuser

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]