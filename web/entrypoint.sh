#!/bin/bash

# Function to start the app
start_app() {
    echo "Starting the application..."
    yarn start &
    APP_PID=$!
}

# Function to stop the app
stop_app() {
    echo "Stopping the application..."
    kill $APP_PID
    wait $APP_PID 2>/dev/null
}

# Navigate to the app directory
cd /app

# Start the app initially
cd web
start_app

# Navigate back to the root directory
cd /app

# Infinite loop to check for updates
while true; do
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

        # Navigate to the web directory
        cd web

        # Install dependencies using Yarn (in case package.json has changed)
        yarn install

        # Rebuild the Next.js application
        yarn build

        # Restart the app
        start_app

        # Navigate back to the root directory
        cd /app
    else
        echo "No new changes detected."
    fi

    # Wait for a specified interval before checking again (e.g., 60 seconds)
    sleep 300
done
