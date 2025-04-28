# Builder stage
FROM python:3.13-alpine AS base

FROM base AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    make

# Install poetry
RUN pip install poetry==2.1.1

# Copy only requirements needed for dependency install
WORKDIR /app
COPY pyproject.toml poetry.lock ./

# Configure poetry to create the virtualenv inside the project directory
# This makes it easier to copy to the final image
RUN poetry config virtualenvs.in-project true

# Install runtime dependencies only 
RUN poetry install --without test --no-root

# Copy source code
COPY src ./src
COPY README.md ./ 

# Build the project
RUN poetry build

# Runtime stage
FROM base AS runtime

# Install runtime dependencies
RUN apk add --no-cache \
    libstdc++

# Create non-root user with Alpine's adduser
RUN adduser -D -u 1000 caqes

WORKDIR /app

# Create config and log directories
RUN mkdir -p /etc/caqes /var/log/caqes && \
    chown -R caqes:caqes /etc/caqes /var/log/caqes

# Copy wheel file and install it
COPY --from=builder /app/dist/*.whl .
RUN pip install *.whl && rm *.whl

# Copy configuration template
COPY caqes.conf.template /etc/caqes/caqes.conf

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CONFIG_PATH=/etc/caqes/caqes.conf
ENV LOG_DIR=/var/log/caqes
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app/src

# Switch to non-root user
USER caqes

# # Create healthcheck script
# COPY --chown=caqes:caqes <<-"EOF" /app/healthcheck.py
# import sys
# from caqes_core.app import CAQES
# try:
#     # Try importing main components
#     from quarantine.quarantine_orchestrator import QuarantineOrchestrator
#     from settings.config import ConfigManager
#     sys.exit(0)
# except Exception as e:
#     print(f"Healthcheck failed: {e}")
#     sys.exit(1)
# EOF

# Add healthcheck
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD python /app/healthcheck.py

# Run the application using the installed package
CMD ["python", "-m", "caqes_core.app"]
