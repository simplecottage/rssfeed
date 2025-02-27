#!/bin/bash

# Create directory structure
mkdir -p frontend/src/components
mkdir -p frontend/public
mkdir -p backend/app
mkdir -p backend/instance

# Move and organize files
cp frontend/nginx.conf frontend/
cp frontend/Dockerfile frontend/
cp backend/Dockerfile backend/

# Create the needed directories
mkdir -p frontend/src/services

# Print setup completion message
echo "Directory structure created!"
echo "Run 'docker-compose up -d' to start the application."
