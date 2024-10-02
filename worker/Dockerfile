FROM python:3.12.4-slim as runner

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . .

# Modify Streamlit's cli.py
RUN STREAMLIT_CLI_PATH=$(poetry run python -c "import streamlit; import os; print(os.path.join(os.path.dirname(streamlit.__file__), 'web', 'cli.py'))") && \
    sed -i '/def _main_run_clExplicit(file, is_hello=False, args=[], flag_options={})/i \
def _main_run_clExplicit(file, is_hello=False, args=[], flag_options={}):\n    bootstrap.run(file, is_hello, args, flag_options)' $STREAMLIT_CLI_PATH

# Expose port 8502
EXPOSE 8502

# Set environment variables (override if needed)
ENV HUB_URL=http://localhost:8000

# Run the executable
CMD ["python run_main.py"]
