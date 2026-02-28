# ========================================
# Quick Start - Simple Chatbot with Backend
# ========================================
# This script starts only the Flask backend for testing chatbot.html

Write-Host "🚀 Starting Simple Chatbot Backend..." -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Setting up backend..." -ForegroundColor Cyan

# Go to backend directory
Set-Location "backend-flask"

# Create venv if needed
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -q flask flask-cors

# Start simple backend
Write-Host ""
Write-Host "🔧 Starting Flask backend on http://localhost:5000..." -ForegroundColor Green
Write-Host ""
Write-Host "📍 You can now use:" -ForegroundColor Cyan
Write-Host "   🌐 chatbot.html - Open file:///G:/My%20Drive/chatbot/mh-chatbot/chatbot.html" -ForegroundColor White
Write-Host "   📝 Dashboard - Open file:///G:/My%20Drive/chatbot/mh-chatbot/index.html" -ForegroundColor White
Write-Host ""
Write-Host "🛑 Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run simple app
python simple_app.py
