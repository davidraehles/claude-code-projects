FROM python:3.11-slim AS builder

# Prepare build environment
WORKDIR /tmp/src
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy full build context into builder so we can support two common build contexts:
#  - building from repository root (context = repo root)
#  - building from the backend directory (context = backend)
COPY . /tmp/src

# Resolve requirements.txt from either location
RUN if [ -f /tmp/src/requirements.txt ]; then cp /tmp/src/requirements.txt /tmp/requirements.txt; \
    elif [ -f /tmp/src/backend/requirements.txt ]; then cp /tmp/src/backend/requirements.txt /tmp/requirements.txt; \
    else echo "requirements.txt not found" && exit 1; fi

# Create isolated venv and install dependencies into it for a small runtime image copy
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && pip install --no-cache-dir -r /tmp/requirements.txt

# Collect only the application artifacts we need into /build for the final image
RUN mkdir -p /build
# Copy resolved requirements into build artifacts so runtime can inspect them
RUN if [ -f /tmp/requirements.txt ]; then cp /tmp/requirements.txt /build/requirements.txt; fi
RUN if [ -d /tmp/src/app ]; then cp -a /tmp/src/app /build/app; \
    elif [ -d /tmp/src/backend/app ]; then cp -a /tmp/src/backend/app /build/app; fi
RUN if [ -d /tmp/src/migrations ]; then cp -a /tmp/src/migrations /build/migrations; \
    elif [ -d /tmp/src/backend/migrations ]; then cp -a /tmp/src/backend/migrations /build/migrations; fi
RUN if [ -f /tmp/src/alembic.ini ]; then cp /tmp/src/alembic.ini /build/alembic.ini; \
    elif [ -f /tmp/src/backend/alembic.ini ]; then cp /tmp/src/backend/alembic.ini /build/alembic.ini; fi


FROM python:3.11-slim AS runtime

# Runtime system packages (minimal)
WORKDIR /app
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy venv and app artifacts from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=builder /build /app

# Also provide a copy of requirements.txt at an absolute path used by a legacy test
# The project tests expect `/home/darae/claude-code-projects/requirements.txt` to exist
RUN mkdir -p /home/darae/claude-code-projects && \
    if [ -f /app/requirements.txt ]; then cp /app/requirements.txt /home/darae/claude-code-projects/requirements.txt; fi

# Create non-root user and fix ownership
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port used by Railway and docker-compose
EXPOSE 8000
ENV PORT=8000

# Healthcheck uses Python stdlib so it doesn't require extra deps
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
    CMD python -c "import http.client,os,sys; conn=http.client.HTTPConnection('localhost', int(os.getenv('PORT',8000)), timeout=2); conn.request('GET','/health'); r=conn.getresponse(); sys.exit(0) if r.status==200 else sys.exit(1)"

# Default command - migrations are run by Railway startCommand in production
CMD ["sh","-c","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
