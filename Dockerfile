FROM python:3.13-slim

# Install dependencies including MariaDB C client
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    build-essential \
    pkg-config \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/usr/local

# Install uv
RUN pip install --no-cache-dir uv

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy project files
COPY pyproject.toml .
COPY uv.lock .
COPY app/ app/
COPY tests/ tests/

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Download NLTK data
RUN [ "uv", "run", "python", "-c", "import nltk; nltk.download('punkt')" ]

# Expose ports for API and Gradio UI
EXPOSE 7860

# Command to run the application
CMD ["uv", "run", "python", "-m", "app.frontend"]
