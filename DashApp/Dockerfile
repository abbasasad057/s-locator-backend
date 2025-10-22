# Use slim image for smaller size and better security
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies required for psycopg2-binary and other packages
RUN apt-get update && \
    apt-get install -y \
    git \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy only the DashApp pyproject so `uv sync` can find project metadata when build context is parent folder
COPY DashApp/pyproject.toml /app/pyproject.toml

# Install dependencies with uv (reads /app/pyproject.toml)
RUN uv sync

# Copy DashApp source into /app
COPY DashApp/ /app/
EXPOSE 8000


# Install dependencies with uv
RUN uv sync 
# Use uv run to execute uvicorn within the virtual environment
CMD ["uv", "run", "python", "dash_app.py"]