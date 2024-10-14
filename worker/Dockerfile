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
RUN git clone -b feature/50b-209-deploy-final-version-of-worker-on-akash https://github.com/agencyenterprise/zerokdb.git

# Navigate to the worker directory
WORKDIR /app/zerokdb/worker

# Disable Poetry virtual environments
RUN poetry config virtualenvs.create false

# Install Python dependencies using Poetry (without virtualenvs)
RUN poetry install --no-root --no-interaction --no-ansi

# Modify Streamlit's cli.py (Ensure Streamlit is installed)
RUN chmod +x /app/zerokdb/worker/update_streamlit.sh && /app/zerokdb/worker/update_streamlit.sh

# Expose port 8502 for the application
EXPOSE 8502

# Set environment variables (override if needed)
ENV HUB_URL=https://g1cqd9cf69e1b0tj8fd7o85mdg.ingress.akashprovid.com
ENV API_HOST=https://kumh6ogteddmj4pgtuh7p00k9c.ingress.akash-palmito.org

# Set the default command
CMD ["sh", "-c", "python run_main.py"]
