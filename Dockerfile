# =============================================================================
# Dockerfile — SAM Backend (FastAPI + Celery)
# =============================================================================
# Multi-stage build for a minimal, secure production image.
# Stage 1: Install dependencies into a virtual environment.
# Stage 2: Copy only the venv and source code into a slim runtime image.
# =============================================================================

# --------------- Stage 1: Builder ---------------
FROM python:3.10-slim AS builder

WORKDIR /build

# Install system-level build dependencies required by psycopg2-binary and
# cryptography. These are only needed at build time.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment inside the builder stage.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies. Copying requirements first leverages Docker
# layer caching — dependencies are only re-installed when requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# --------------- Stage 2: Runtime ---------------
FROM python:3.10-slim AS runtime

# Metadata
LABEL maintainer="SAM Project"
LABEL description="SAM Backend — FastAPI API Server & Celery Workers"

# Install only the minimal runtime libraries (libpq for PostgreSQL driver).
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security best practices.
RUN groupadd --gid 1000 sam && \
    useradd --uid 1000 --gid sam --shell /bin/bash --create-home sam

WORKDIR /app

# Copy the pre-built virtual environment from the builder stage.
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
# so that logs appear immediately in `docker logs`.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Copy application source code.
COPY backend/ ./backend/
COPY requirements.txt .

# Create necessary runtime directories with correct ownership.
RUN mkdir -p /app/temp_audio /app/tmp && \
    chown -R sam:sam /app

# Switch to the non-root user.
USER sam

# Expose the API port. The actual port is controlled by the CMD/entrypoint.
EXPOSE 8000

# Health check — Gunicorn/Uvicorn serves the FastAPI root endpoint.
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Default command: Start the FastAPI server with Gunicorn + Uvicorn workers.
# This can be overridden in docker-compose.yml for the Celery worker/beat services.
CMD ["gunicorn", "backend.main:app", \
     "--workers", "2", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
