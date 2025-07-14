#!/bin/bash

# RAG-Based MCP Ticketing System - Quick Setup Script
# This script helps you set up the project quickly on your local machine

set -e  # Exit on any error

echo "🚀 RAG-Based MCP Ticketing System - Quick Setup"
echo "================================================="

# Check Python version
echo "📋 Checking prerequisites..."
python_version=$(python --version 2>&1 | cut -d' ' -f2)
echo "✅ Python version: $python_version"

if ! python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    echo "❌ Error: Python 3.10+ is required. Please upgrade Python."
    exit 1
fi

# Create virtual environment
echo "🏗️  Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate || .venv\Scripts\activate.bat

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt

# Install client dependencies
echo "📦 Installing client dependencies..."
cd client
pip install -r requirements.txt
cd ..

# Setup environment files
echo "⚙️  Setting up environment configuration..."

# Backend .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created backend .env file from template"
    echo "⚠️  Please edit .env and add your Azure OpenAI credentials"
else
    echo "✅ Backend .env file already exists"
fi

# Client .env
if [ ! -f "client/.env" ]; then
    cp client/.env.example client/.env
    echo "✅ Created client .env file from template"
    echo "⚠️  Please edit client/.env and add your Azure OpenAI credentials"
else
    echo "✅ Client .env file already exists"
fi

# Create logs directory
mkdir -p logs
echo "✅ Created logs directory"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env files with your Azure OpenAI credentials:"
echo "   - Edit .env (backend configuration)"
echo "   - Edit client/.env (frontend configuration)"
echo ""
echo "2. Start the MCP server (backend):"
echo "   python -m app.main"
echo ""
echo "3. In another terminal, start the client (frontend):"
echo "   cd client && python main.py"
echo ""
echo "4. Open your browser to: http://localhost:8001"
echo ""
echo "📚 For detailed instructions, see README.md"
echo "🐛 For troubleshooting, see the 'Troubleshooting' section in README.md"
