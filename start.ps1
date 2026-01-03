# Quick Start Script for Full System Integration (Windows PowerShell)
# This script checks and starts all components

Write-Host "`n🚀 Dayflow HRMS - System Startup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

Write-Host "`n📋 Checking Prerequisites...`n" -ForegroundColor Yellow

# Check MongoDB
try {
    $mongoCheck = Get-Process mongod -ErrorAction SilentlyContinue
    if ($mongoCheck) {
        Write-Host "✅ MongoDB is running" -ForegroundColor Green
    } else {
        Write-Host "⚠️  MongoDB not running. Start it with: mongod" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ MongoDB not found" -ForegroundColor Red
    Write-Host "   Install from: https://www.mongodb.com/try/download/community" -ForegroundColor Gray
}

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not installed" -ForegroundColor Red
}

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js installed: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not installed" -ForegroundColor Red
}

# Check npm
try {
    $npmVersion = npm --version
    Write-Host "✅ npm installed: v$npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not installed" -ForegroundColor Red
}

Write-Host "`n🔧 Checking Project Setup...`n" -ForegroundColor Yellow

# Check virtual environment
if (Test-Path "venv") {
    Write-Host "✅ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  Virtual environment not found" -ForegroundColor Yellow
    Write-Host "   Creating virtual environment..." -ForegroundColor Gray
    python -m venv venv
}

# Check node_modules
if (Test-Path "node_modules") {
    Write-Host "✅ Node modules installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  Node modules not installed" -ForegroundColor Yellow
    Write-Host "   Run: npm install" -ForegroundColor Gray
}

# Check .env
if (Test-Path ".env") {
    Write-Host "✅ Backend .env file exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  Backend .env not found" -ForegroundColor Yellow
    Write-Host "   Create .env with MongoDB and secret key configuration" -ForegroundColor Gray
}

Write-Host "`n🎯 Next Steps:`n" -ForegroundColor Cyan

Write-Host "1️⃣  Start MongoDB:" -ForegroundColor White
Write-Host "   mongod" -ForegroundColor Gray
Write-Host ""

Write-Host "2️⃣  Start Backend (in new PowerShell terminal):" -ForegroundColor White
Write-Host "   cd c:\Users\Admin\OneDrive\Desktop\odduBackend\OdooXGcet" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python main.py" -ForegroundColor Gray
Write-Host ""

Write-Host "3️⃣  Start Frontend (in new PowerShell terminal):" -ForegroundColor White
Write-Host "   cd c:\Users\Admin\OneDrive\Desktop\odduBackend\OdooXGcet" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""

Write-Host "4️⃣  Run E2E Tests (optional):" -ForegroundColor White
Write-Host "   pytest test_e2e_connection.py -v" -ForegroundColor Gray
Write-Host ""

Write-Host "5️⃣  Access Application:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "   Backend API: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to install dependencies
$response = Read-Host "Would you like to install testing dependencies now? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "`n📦 Installing testing dependencies..." -ForegroundColor Yellow
    
    # Activate virtual environment
    & .\venv\Scripts\Activate.ps1
    
    # Install dependencies
    pip install -r requirements-test.txt
    playwright install chromium
    
    Write-Host "`n✅ Testing dependencies installed!" -ForegroundColor Green
}

Write-Host "`n✨ Setup check complete!" -ForegroundColor Cyan
