FROM python:3.12-slim AS base
FROM base AS builder

# Install poetry
RUN python3 -m pip install poetry==2.1.1
ENV POETRY_VIRTUALENVS_CREATE=false

# Set work directory
WORKDIR /app

# Copy and install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --only=main --no-root --no-interaction --no-ansi

# Copy application code
COPY ./src/ .

# Stage 2: Runtime
FROM base AS final

# Copy installed dependencies from builder
COPY --from=builder /usr/local /usr/local

# Add non-root user
RUN adduser --disabled-password caqes
USER caqes

# Set work directory
WORKDIR /src

ENV PYTHON_PATH=/src

# Copy application code
COPY --from=builder /app /src

# Set the default command
CMD ["python","caqes_core/app.py"]
