# Chatbot Startup Script
Write-Host "🚀 Starting Mental Health Chatbot..." -ForegroundColor Cyan

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
& "G:\My Drive\chatbot\.venv\Scripts\Activate.ps1"

# Install required packages
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
& "G:\My Drive\chatbot\.venv\Scripts\pip.exe" install flask flask-cors google-generativeai python-dotenv

# Navigate to backend directory
Set-Location "G:\My Drive\chatbot\mh-chatbot\backend-flask"

# Run the chatbot
Write-Host "🎉 Starting Flask server..." -ForegroundColor Green
Write-Host "🌐 Open http://localhost:5000 in your browser" -ForegroundColor Cyan
& "G:\My Drive\chatbot\.venv\Scripts\python.exe" final_working_chat.py
