#!/bin/bash
# Aideck Development Startup Script
# This script starts the Aideck application in development mode

set -e

echo "🚀 Starting Aideck in development mode..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Please run ./setup.sh first."
    exit 1
fi

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
fi

# Set environment variables for development
export DEBUG=true
export LOG_LEVEL=INFO

# Start the application
echo "🎯 Starting Aideck..."
echo "📱 The application will be available at http://localhost:7541"
echo "📚 API documentation will be available at http://localhost:7541"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start Flask server
uv run python -c "from src.aideck.start import start; start(api=True)"
