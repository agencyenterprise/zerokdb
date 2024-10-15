#!/bin/bash

# Function to clone or update the repository
update_repo() {
    if [ ! -d "/app/zerokdb" ]; then
        echo "Cloning repository..."
        git clone -b main https://github.com/agencyenterprise/zerokdb.git /app/zerokdb
    else
        echo "Repository already cloned. Pulling latest changes..."
        cd /app/zerokdb || exit 1
        git pull origin main
    fi
}

# Function to build the app
build_app() {
    echo "Building the application..."
    cd /app/zerokdb/worker || exit 1
    poetry config virtualenvs.create false
    poetry lock
    poetry install --no-root --no-interaction --no-ansi
    chmod +x /app/zerokdb/worker/update_streamlit.sh
    /app/zerokdb/worker/update_streamlit.sh
    echo "Application built successfully."
}

# Function to start the app
start_app() {
    echo "Starting the application..."
    cd /app/zerokdb/worker || exit 1
    python run_main.py &
    APP_PID=$!
    echo "Application started with PID $APP_PID"
}

# Function to stop the app
stop_app() {
    APP_PID=$(pgrep -f 'python run_main.py')
    if [ -n "$APP_PID" ]; then
        echo "Stopping application with PID $APP_PID"
        kill $APP_PID
        wait $APP_PID 2>/dev/null
        echo "Application stopped."
    else
        echo "No running application found."
    fi
}

# Initial setup and start
update_repo
build_app
start_app

# Check for updates in a loop
while true; do
    sleep 300  # Interval between checks

    echo "Checking for repository updates..."
    cd /app/zerokdb || exit 1
    git fetch origin main

    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)

    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "New changes detected. Updating application..."
        stop_app
        git pull origin main
        build_app
        start_app
    else
        echo "No new changes detected."
    fi
done
