# ========================================
# Complete Application Launcher - Production Ready
# ========================================
# Starts authentication backend + React frontend

Write-Host ""
Write-Host "🚀 Starting Mental Health Chatbot - Full Application" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "📋 Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "📋 Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Node.js not found. Please install Node.js 14+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔧 Setting up backend..." -ForegroundColor Cyan
Set-Location "backend-flask"

# Install minimal dependencies
Write-Host "   Installing Python dependencies..." -ForegroundColor Yellow
pip install -q -r requirements-minimal.txt

# Start backend
Write-Host "   Starting authentication backend on port 5000..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location "G:\My Drive\chatbot\mh-chatbot\backend-flask"
    python auth_app.py
}

Write-Host "   Backend Job ID: $($backendJob.Id)" -ForegroundColor Gray
Start-Sleep -Seconds 5

# Go to frontend
Set-Location "..\frontend"

Write-Host ""
Write-Host "🌐 Setting up frontend..." -ForegroundColor Cyan

# Check if node_modules exists
if (!(Test-Path "node_modules")) {
    Write-Host "   Installing npm dependencies (first time - may take a few minutes)..." -ForegroundColor Yellow
    npm install
}
else {
    Write-Host "   Dependencies already installed ✓" -ForegroundColor Green
}

# Start React frontend
Write-Host "   Starting React application on port 3000..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "G:\My Drive\chatbot\mh-chatbot\frontend"
    $env:BROWSER = "none"
    npm start
}

Write-Host "   Frontend Job ID: $($frontendJob.Id)" -ForegroundColor Gray
Write-Host "   Waiting for React to compile..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Green
Write-Host "✅ APPLICATION IS READY!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access the application:" -ForegroundColor Cyan
Write-Host "   http://localhost:3000" -ForegroundColor White -BackgroundColor Blue
Write-Host ""
Write-Host "👤 Login with these accounts:" -ForegroundColor Cyan
Write-Host "   📧 Admin:  admin@example.com" -ForegroundColor White
Write-Host "   🔑 Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "   📧 User:   user@example.com" -ForegroundColor White
Write-Host "   🔑 Password: user123" -ForegroundColor White
Write-Host ""
Write-Host "📍 Backend API: http://localhost:5000" -ForegroundColor Gray
Write-Host ""
Write-Host "🎯 After login, you can access:" -ForegroundColor Cyan
Write-Host "   • Chat with voice support" -ForegroundColor White
Write-Host "   • Journal entries" -ForegroundColor White
Write-Host "   • Mental health features" -ForegroundColor White
Write-Host "   • Admin dashboard (admin only)" -ForegroundColor White
Write-Host ""

# Open browser
Write-Host "🌐 Opening browser..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "✅ Browser opened to LOGIN PAGE" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Monitor logs:" -ForegroundColor Yellow
Write-Host "   Backend:  Receive-Job -Id $($backendJob.Id) -Keep" -ForegroundColor Gray
Write-Host "   Frontend: Receive-Job -Id $($frontendJob.Id) -Keep" -ForegroundColor Gray
Write-Host ""
Write-Host "🛑 To stop: Press Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Keep script running
try {
    while ($true) {
        $backendState = Get-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
        $frontendState = Get-Job -Id $frontendJob.Id -ErrorAction SilentlyContinue
        
        if ($backendState.State -eq "Failed") {
            Write-Host ""
            Write-Host "❌ Backend failed!" -ForegroundColor Red
            Receive-Job -Id $backendJob.Id
            break
        }
        
        if ($frontendState.State -eq "Failed") {
            Write-Host ""
            Write-Host "❌ Frontend failed!" -ForegroundColor Red
            Receive-Job -Id $frontendJob.Id
            break
        }
        
        Start-Sleep -Seconds 2
    }
}
finally {
    Write-Host ""
    Write-Host "🛑 Stopping services..." -ForegroundColor Red
    Stop-Job -Id $backendJob.Id, $frontendJob.Id -ErrorAction SilentlyContinue
    Remove-Job -Id $backendJob.Id, $frontendJob.Id -Force -ErrorAction SilentlyContinue
    Write-Host "✅ All services stopped." -ForegroundColor Green
}
