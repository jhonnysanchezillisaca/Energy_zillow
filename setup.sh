#!/bin/bash
set -euo pipefail

# One-time setup script for Proxmox LXC
# Run this after manually creating the LXC with Docker

REPO_URL="https://github.com/jhonnysanchezillisaca/Energy_zillow.git"
BRANCH="refactor"
APP_DIR="$HOME/Energy_zillow"

echo "=== Energy Zillow API - One-time Setup ==="
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    echo "You can use the Proxmox helper script from: https://community-scripts.org/scripts/docker"
    exit 1
fi

# Check if docker compose is available
if ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not installed."
    exit 1
fi

# Clone the repository if it doesn't exist
if [ ! -d "$APP_DIR" ]; then
    echo "Cloning repository from $REPO_URL..."
    git clone -b "$BRANCH" "$REPO_URL" "$APP_DIR"
    echo "Repository cloned successfully."
else
    echo "Repository already exists at $APP_DIR"
fi

cd "$APP_DIR"

# Create .env from template if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your secrets:"
    echo "   - OPENAI_API_KEY (required for recommendations)"
    echo "   - CLOUDFLARE_TUNNEL_TOKEN (required for public access)"
    echo "   - CORS_ORIGINS (add your Vercel frontend URL)"
    echo ""
    echo "Edit .env with: nano $APP_DIR/.env"
    echo ""
    echo "After editing .env, run: ./deploy.sh"
    exit 0
fi

# Check if required secrets are set
if grep -q "your_openai_api_key_here" .env || grep -q "your_cloudflare_tunnel_token_here" .env; then
    echo "⚠️  WARNING: .env still contains placeholder values."
    echo "   Please edit .env and add your real secrets."
    echo "   Edit .env with: nano $APP_DIR/.env"
    exit 1
fi

# Start the application
echo "Starting application with Docker Compose..."
docker compose up --build -d

echo ""
echo "=== Setup complete ==="
echo "API is running at: http://localhost:8000"
echo "Health check: http://localhost:8000/health"
echo ""
echo "To update the application later, run: ./deploy.sh"
echo "To view logs: docker compose logs -f"
echo "To stop: docker compose down"
