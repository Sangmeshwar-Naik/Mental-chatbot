# ========================================
# Start Mental Health Chatbot - PowerShell Script
# ========================================
# This script starts both the Flask backend and React frontend

Write-Host "🚀 Starting Mental Health Chatbot..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
Write-Host "Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 14+ first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Setting up backend..." -ForegroundColor Cyan

# Navigate to backend directory
Set-Location "backend-flask"

# Check if virtual environment exists
if (!(Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -q flask flask-cors flask-sqlalchemy flask-login python-dotenv

# Check if .env exists
if (!(Test-Path ".env")) {
    Write-Host "⚠️  Creating .env file..." -ForegroundColor Yellow
    @"
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///mental_health.db
"@ | Set-Content ".env"
}

# Start Flask backend in background
Write-Host "🔧 Starting Flask backend on http://localhost:5000..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location "G:\My Drive\chatbot\mh-chatbot\backend-flask"
    .\venv\Scripts\Activate.ps1
    python app.py
}

# Wait for backend to start
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Navigate back and go to frontend
Set-Location ".."

Write-Host ""
Write-Host "📦 Setting up frontend..." -ForegroundColor Cyan
Set-Location "frontend"

# Install npm dependencies if needed
if (!(Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    npm install
}

# Start React frontend in background
Write-Host "🌐 Starting React frontend on http://localhost:3000..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "G:\My Drive\chatbot\mh-chatbot\frontend"
    npm start
}

# Wait for frontend to compile
Write-Host "⏳ Waiting for frontend to compile..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "✅ Services are running!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Access points:" -ForegroundColor Cyan
Write-Host "   🌐 Frontend (Login Page): http://localhost:3000" -ForegroundColor White
Write-Host "   🔧 Backend API: http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "📊 To view logs:" -ForegroundColor Yellow
Write-Host "   Backend: Receive-Job $($backendJob.Id) -Keep" -ForegroundColor White
Write-Host "   Frontend: Receive-Job $($frontendJob.Id) -Keep" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop services:" -ForegroundColor Yellow
Write-Host "   Press Ctrl+C and run: Stop-Job -Id $($backendJob.Id),$($frontendJob.Id); Remove-Job -Id $($backendJob.Id),$($frontendJob.Id)" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Opening browser in 3 seconds..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Open browser
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "✅ Application is ready! Check your browser." -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop all services when done." -ForegroundColor Yellow

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    # Cleanup jobs on exit
    Write-Host ""
    Write-Host "🛑 Stopping services..." -ForegroundColor Red
    Stop-Job -Id $backendJob.Id, $frontendJob.Id
    Remove-Job -Id $backendJob.Id, $frontendJob.Id
    Write-Host "✅ All services stopped." -ForegroundColor Green
}
