# Use an official Python runtime as a parent image
FROM python:3.12.4-slim as runner

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies, including libpq-dev for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Clone the zerokdb repository
RUN git clone https://github.com/agencyenterprise/zerokdb.git

# Navigate to the API directory
WORKDIR /app/zerokdb/zerokdbapi

# Disable Poetry virtual environments
RUN poetry config virtualenvs.create false

# Install Python dependencies using Poetry (without virtualenvs)
RUN poetry install --no-root --no-interaction --no-ansi

# Expose port 8001 for the FastAPI application
EXPOSE 8001

# Set default environment variables (can be overridden by .env file)
ENV API_HOST=http://localhost:8001

# Define the default command to run the FastAPI application with Uvicorn
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
