#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to build the app
build_app() {
    echo "Building the application..."
    cd /app/zerokdb/zerokdbapi

    # Configure Poetry to not create virtual environments
    poetry config virtualenvs.create false

    # Install dependencies using Poetry
    poetry lock
    poetry install

    echo "Application built successfully."
}

# Function to start the app
start_app() {
    echo "Starting the application..."
    cd /app/zerokdb/zerokdbapi
    uvicorn main:app --host 0.0.0.0 --port 8001 &
    APP_PID=$!
    echo "Application started with PID $APP_PID"
}

# Function to stop the app
stop_app() { 
    APP_PID=$(netstat -tnpl 2>/dev/null | grep ':8001' | awk '{print $7}' | cut -d'/' -f1)
    echo "Stopping application with PID $APP_PID"
    kill $APP_PID
    wait $APP_PID 2>/dev/null || true
    echo "Application with PID $APP_PID stopped."
}

# Clone the repository if not already cloned
if [ ! -d "/app/zerokdb" ]; then
    echo "Cloning repository..."
    git clone https://github.com/agencyenterprise/zerokdb.git /app/zerokdb
else
    echo "Repository already cloned."
fi

# Build the app initially
build_app

# Start the app initially
start_app

# Trap SIGTERM and SIGINT to gracefully stop the app
trap stop_app SIGTERM SIGINT

# Infinite loop to check for updates
while true; do
    # Wait for a specified interval before checking for updates (e.g., 300 seconds)
    sleep 300

    # Navigate to the repository directory
    cd /app/zerokdb

    # Fetch latest changes from the repo
    git fetch origin main

    # Check if there are new commits
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)

    if [ "$LOCAL" != "$REMOTE" ]; then
        echo "New changes detected. Updating application..."

        # Stop the running app
        stop_app

        # Pull the latest changes
        git pull origin main

        # Rebuild the application
        build_app

        # Restart the app
        start_app
    else
        echo "No new changes detected."
    fi

    # Navigate back to the root directory
    cd /app
done
