# Use an official Python 3.12.4 slim image as the base
FROM python:3.12.4-slim

# Set environment variables to prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    libpq-dev \
    net-tools \
    openssh-client \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Verify Poetry installation
RUN poetry --version

# Pre clone repo
RUN git clone https://github.com/agencyenterprise/zerokdb.git /app/zerokdb
WORKDIR /app/zerokdb/zerokdbapi

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false
RUN poetry lock
RUN poetry install

WORKDIR /app

# Copy the entrypoint script into the container
COPY entrypoint.sh /entrypoint.sh

# Ensure the entrypoint script has Unix line endings
RUN dos2unix /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Expose port 8001 for the FastAPI application
EXPOSE 8001

# Set the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]
