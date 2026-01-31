#!/bin/bash
# Aideck Development Environment Setup Script
# This script sets up the development environment for the Aideck project

set -e

echo "🚀 Setting up Aideck development environment..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "🐍 Python version: $PYTHON_VERSION"

if [[ "$(python3 -c 'import sys; print(sys.version_info[0])')" -lt 3 ]]; then
    echo "❌ Error: Python 3.10 or higher is required"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Install dependencies
echo "📦 Installing project dependencies..."
uv sync --extra dev --extra rag --extra storage

# Set up environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your API keys!"
    echo "   - OPENAI_API_KEY"
    echo "   - ANTHROPIC_API_KEY (optional)"
    echo "   - SECRET_KEY"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p data

# Install pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
uv run pre-commit install

# Run tests to verify setup
echo "🧪 Running tests to verify setup..."
uv run pytest --version

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "   uv run python -m aideck"
echo ""
echo "🔧 To run tests:"
echo "   uv run pytest"
echo ""
echo "📝 To run linting:"
echo "   uv run pre-commit run --all-files"
echo ""
echo "⚠️  Don't forget to:"
echo "   1. Edit .env file with your API keys"
echo "   2. Run 'uv run python -m aideck' to start the application"
