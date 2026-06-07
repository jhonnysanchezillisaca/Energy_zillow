#!/bin/bash
set -euo pipefail

# Deployment script for Proxmox LXC
# Run this to update the application to the latest version

APP_DIR="$HOME/Energy_zillow"
BRANCH="refactor"

echo "=== Energy Zillow API - Deploy ==="
echo

# Check if the app directory exists
if [ ! -d "$APP_DIR" ]; then
    echo "Error: App directory not found at $APP_DIR"
    echo "Please run setup.sh first."
    exit 1
fi

cd "$APP_DIR"

# Check if .env exists with real secrets
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please run setup.sh first."
    exit 1
fi

if grep -q "your_openai_api_key_here" .env || grep -q "your_cloudflare_tunnel_token_here" .env; then
    echo "⚠️  WARNING: .env still contains placeholder values."
    echo "   Please edit .env and add your real secrets before deploying."
    exit 1
fi

# Pull latest changes from git
echo "Pulling latest changes from branch '$BRANCH'..."
git fetch origin "$BRANCH"
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "@{u}")

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "Already up to date."
else
    echo "New changes found. Pulling..."
    git pull origin "$BRANCH"
fi

# Rebuild and restart containers
echo "Building and restarting containers..."
docker compose up --build -d

# Clean up old images to save space
echo "Cleaning up old Docker images..."
docker image prune -f --filter "dangling=true"

echo ""
echo "=== Deploy complete ==="
echo "API is running at: http://localhost:8000"
echo "Health check: http://localhost:8000/health"
echo ""
echo "To view logs: docker compose logs -f"
echo "To view API logs: docker compose logs -f api"
echo "To view tunnel logs: docker compose logs -f tunnel"
echo "To stop: docker compose down"
