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

# Copy uv configuration files
COPY pyproject.toml uv.lock ./

# Install dependencies with uv
RUN uv sync --frozen

COPY . /app
EXPOSE 8000

# Use uv run to execute uvicorn within the virtual environment
CMD ["uv", "run", "uvicorn", "run_apps:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]