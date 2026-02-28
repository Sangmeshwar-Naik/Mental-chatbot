# ========================================
# Complete Application Launcher
# ========================================
# Starts Flask backend + React frontend with login page

Write-Host ""
Write-Host "🚀 Starting Complete Mental Health Platform..." -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Function to check if port is in use
function Test-Port {
    param($Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
    return $connection
}

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Node.js not found. Please install Node.js 14+" -ForegroundColor Red
    exit 1
}

# Check if ports are available
if (Test-Port 5000) {
    Write-Host "⚠️  Port 5000 is already in use" -ForegroundColor Yellow
    Write-Host "   This might be the backend from a previous run" -ForegroundColor Yellow
    $response = Read-Host "   Continue anyway? (y/n)"
    if ($response -ne 'y') {
        exit 1
    }
}

if (Test-Port 3000) {
    Write-Host "⚠️  Port 3000 is already in use" -ForegroundColor Yellow
    $response = Read-Host "   Continue anyway? (y/n)"
    if ($response -ne 'y') {
        exit 1
    }
}

Write-Host ""
Write-Host "🔧 Setting up backend..." -ForegroundColor Cyan

# Navigate to backend
Set-Location "backend-flask"

# Create/activate virtual environment
if (!(Test-Path "venv")) {
    Write-Host "   Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "   Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install backend dependencies
Write-Host "   Installing Python dependencies..." -ForegroundColor Yellow
pip install -q flask flask-cors flask-sqlalchemy flask-login werkzeug python-dotenv

# Initialize database
Write-Host "   Initializing database..." -ForegroundColor Yellow
python init_db.py

# Start backend in background
Write-Host "   Starting Flask backend on http://localhost:5000..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location "G:\My Drive\chatbot\mh-chatbot\backend-flask"
    .\venv\Scripts\Activate.ps1
    $env:FLASK_APP = "app.py"
    $env:FLASK_ENV = "development"
    python app.py
}

Write-Host "   Backend process ID: $($backendJob.Id)" -ForegroundColor Gray

# Wait for backend to start
Write-Host "   Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Navigate to frontend
Set-Location ".."
Set-Location "frontend"

Write-Host ""
Write-Host "🌐 Setting up frontend..." -ForegroundColor Cyan

# Install npm dependencies if needed
if (!(Test-Path "node_modules")) {
    Write-Host "   Installing npm dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    npm install
}

# Start React frontend
Write-Host "   Starting React frontend on http://localhost:3000..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "G:\My Drive\chatbot\mh-chatbot\frontend"
    $env:BROWSER = "none"  # Don't auto-open browser
    npm start
}

Write-Host "   Frontend process ID: $($frontendJob.Id)" -ForegroundColor Gray

# Wait for frontend to compile
Write-Host "   Waiting for frontend to compile..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "✅ PLATFORM IS READY!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "📍 Access Points:" -ForegroundColor Cyan
Write-Host "   🌐 Frontend (Login): http://localhost:3000" -ForegroundColor White
Write-Host "   🔧 Backend API:      http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "👤 Default Accounts:" -ForegroundColor Cyan
Write-Host "   Admin:  admin@example.com / admin123" -ForegroundColor White
Write-Host "   User:   user@example.com / user123" -ForegroundColor White
Write-Host ""
Write-Host "📊 To view logs:" -ForegroundColor Yellow
Write-Host "   Backend:  Receive-Job $($backendJob.Id) -Keep" -ForegroundColor White
Write-Host "   Frontend: Receive-Job $($frontendJob.Id) -Keep" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop all services:" -ForegroundColor Yellow
Write-Host "   Press Ctrl+C, then run:" -ForegroundColor White
Write-Host "   Stop-Job $($backendJob.Id),$($frontendJob.Id); Remove-Job $($backendJob.Id),$($frontendJob.Id)" -ForegroundColor Gray
Write-Host ""

# Open browser
Write-Host "🌐 Opening browser in 3 seconds..." -ForegroundColor Cyan
Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "✅ Application is running! Check your browser." -ForegroundColor Green
Write-Host "   You should see the LOGIN page." -ForegroundColor White
Write-Host ""
Write-Host "📝 After logging in, you can access:" -ForegroundColor Cyan
Write-Host "   • AI Chat with voice support" -ForegroundColor White
Write-Host "   • Journal entries" -ForegroundColor White
Write-Host "   • Mental health screenings" -ForegroundColor White
Write-Host "   • Admin dashboard (admin account only)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C when you want to stop all services." -ForegroundColor Yellow
Write-Host ""

# Store job IDs globally
$Global:BackendJobId = $backendJob.Id
$Global:FrontendJobId = $frontendJob.Id

# Keep script running
try {
    while ($true) {
        # Check if jobs are still running
        $backendStatus = Get-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
        $frontendStatus = Get-Job -Id $frontendJob.Id -ErrorAction SilentlyContinue
        
        if ($backendStatus.State -eq "Failed" -or $frontendStatus.State -eq "Failed") {
            Write-Host ""
            Write-Host "⚠️  A service has failed!" -ForegroundColor Red
            if ($backendStatus.State -eq "Failed") {
                Write-Host "Backend error:" -ForegroundColor Red
                Receive-Job -Id $backendJob.Id
            }
            if ($frontendStatus.State -eq "Failed") {
                Write-Host "Frontend error:" -ForegroundColor Red
                Receive-Job -Id $frontendJob.Id
            }
            break
        }
        
        Start-Sleep -Seconds 2
    }
}
finally {
    # Cleanup on exit
    Write-Host ""
    Write-Host "🛑 Stopping services..." -ForegroundColor Red
    Stop-Job -Id $backendJob.Id, $frontendJob.Id -ErrorAction SilentlyContinue
    Remove-Job -Id $backendJob.Id, $frontendJob.Id -Force -ErrorAction SilentlyContinue
    Write-Host "✅ All services stopped." -ForegroundColor Green
}
