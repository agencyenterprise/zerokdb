#!/bin/bash

# Function to build the app
build_app() {
    echo "Building the application..."
    cd /app/web
    yarn build
    echo "Application built successfully."
}

# Function to start the app
start_app() {
    echo "Starting the application..."
    cd /app/web
    yarn start &
    APP_PID=$!
    echo "Application started with PID $APP_PID"
}

# Function to stop the app
stop_app() {
    APP_PID=$(netstat -tnpl 2>/dev/null | grep ':3000' | awk '{print $7}' | cut -d'/' -f1)
    echo "Stopping application with PID $APP_PID"
    kill $APP_PID
    wait $APP_PID 2>/dev/null
    echo "Application with PID $APP_PID stopped."
}

# Build the app initially
build_app

# Start the app initially
start_app

# Infinite loop to check for updates
while true; do
    # Wait for a specified interval before checking for updates (e.g., 300 seconds)
    sleep 300

    # Navigate to the app directory
    cd /app

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

        # Install dependencies in case package.json has changed
        cd /app/web
        yarn install

        # Rebuild the application
        build_app

        # Restart the app
        start_app
    else
        echo "No new changes detected."
    fi
done
