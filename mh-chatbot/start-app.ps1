# Mental Health Chatbot - Complete Application Launcher
# Starts the Flask backend with authentication and all features

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Mental Health Chatbot - Starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to backend directory
Set-Location "backend-flask"

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "[✓] Virtual environment found" -ForegroundColor Green
}
else {
    Write-Host "[!] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "[→] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies if needed
if (!(Test-Path "venv\Lib\site-packages\flask")) {
    Write-Host "[→] Installing dependencies..." -ForegroundColor Yellow
    pip install flask flask-cors google-generativeai python-dotenv
}

# Check for .env file
if (!(Test-Path ".env")) {
    Write-Host "" 
    Write-Host "[!] WARNING: .env file not found!" -ForegroundColor Red
    Write-Host "    Create a .env file with your GEMINI_API_KEY" -ForegroundColor Red
    Write-Host ""
}

# Start the Flask application
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Starting Flask Server..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Application will be available at:" -ForegroundColor Cyan
Write-Host "   http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "📱 Features:" -ForegroundColor Cyan
Write-Host "   - Login/Signup System" -ForegroundColor White
Write-Host "   - Mental Health Tools" -ForegroundColor White
Write-Host "   - Wellness & Relaxation" -ForegroundColor White
Write-Host "   - 6 Cognitive Games" -ForegroundColor White
Write-Host "   - AI Chatbot" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the Flask app
python final_working_chat.py
