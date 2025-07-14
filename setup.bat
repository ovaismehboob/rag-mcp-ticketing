@echo off
REM RAG-Based MCP Ticketing System - Quick Setup Script for Windows
REM This script helps you set up the project quickly on your Windows machine

echo 🚀 RAG-Based MCP Ticketing System - Quick Setup
echo =================================================

REM Check Python version
echo 📋 Checking prerequisites...
python --version
if %errorlevel% neq 0 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo 🏗️  Creating virtual environment...
if not exist ".venv" (
    python -m venv .venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install backend dependencies
echo 📦 Installing backend dependencies...
pip install -r requirements.txt

REM Install client dependencies
echo 📦 Installing client dependencies...
cd client
pip install -r requirements.txt
cd ..

REM Setup environment files
echo ⚙️  Setting up environment configuration...

REM Backend .env
if not exist ".env" (
    copy .env.example .env
    echo ✅ Created backend .env file from template
    echo ⚠️  Please edit .env and add your Azure OpenAI credentials
) else (
    echo ✅ Backend .env file already exists
)

REM Client .env
if not exist "client\.env" (
    copy client\.env.example client\.env
    echo ✅ Created client .env file from template
    echo ⚠️  Please edit client\.env and add your Azure OpenAI credentials
) else (
    echo ✅ Client .env file already exists
)

REM Create logs directory
if not exist "logs" mkdir logs
echo ✅ Created logs directory

echo.
echo 🎉 Setup completed successfully!
echo.
echo 📝 Next steps:
echo 1. Edit .env files with your Azure OpenAI credentials:
echo    - Edit .env (backend configuration)
echo    - Edit client\.env (frontend configuration)
echo.
echo 2. Start the MCP server (backend):
echo    python -m app.main
echo.
echo 3. In another terminal, start the client (frontend):
echo    cd client ^&^& python main.py
echo.
echo 4. Open your browser to: http://localhost:8001
echo.
echo 📚 For detailed instructions, see README.md
echo 🐛 For troubleshooting, see the 'Troubleshooting' section in README.md
echo.
pause
