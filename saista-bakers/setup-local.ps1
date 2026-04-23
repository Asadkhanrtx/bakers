# Saista Bakers - Local Setup Script for Windows PowerShell
# This script automates the setup process

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          Saista Bakers - Local Development Setup             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Python
$pythonInstalled = $null -ne (Get-Command python -ErrorAction SilentlyContinue)
if ($pythonInstalled) {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Download from https://www.python.org/downloads/" -ForegroundColor Red
    exit
}

# Check Node.js
$nodeInstalled = $null -ne (Get-Command node -ErrorAction SilentlyContinue)
if ($nodeInstalled) {
    $nodeVersion = node --version
    Write-Host "✓ Node.js: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Node.js not found. Download from https://nodejs.org/" -ForegroundColor Red
    exit
}

# Check MySQL
$mysqlInstalled = $null -ne (Get-Command mysql -ErrorAction SilentlyContinue)
if ($mysqlInstalled) {
    Write-Host "✓ MySQL found" -ForegroundColor Green
} else {
    Write-Host "✗ MySQL not found. Download from https://dev.mysql.com/downloads/mysql/" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "All prerequisites found!" -ForegroundColor Green
Write-Host ""

# Get project root
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# Step 1: Setup MySQL Database
Write-Host "Step 1: Setting up MySQL database..." -ForegroundColor Yellow
try {
    $mysqlCmd = "mysql -u root -p`"$mysqlPassword`" < `"$projectRoot\database\schema.sql`""
    Write-Host "Please enter your MySQL root password (press Enter if no password):"
    $mysqlPassword = Read-Host "MySQL password" -AsSecureString
    $mysqlPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($mysqlPassword))
    
    if ([string]::IsNullOrEmpty($mysqlPassword)) {
        mysql -u root < "$projectRoot\database\schema.sql" 2>$null
    } else {
        mysql -u root -p"$mysqlPassword" < "$projectRoot\database\schema.sql" 2>$null
    }
    Write-Host "✓ Database schema imported" -ForegroundColor Green
} catch {
    Write-Host "⚠ Could not import database. You may need to do this manually." -ForegroundColor Yellow
    Write-Host "  Run: mysql -u root -p < database/schema.sql" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Setup User Service
Write-Host "Step 2: Setting up User Service (Flask)..." -ForegroundColor Yellow

$userServicePath = Join-Path $projectRoot "user-service"
Set-Location $userServicePath

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt -q
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Create .env file
$envContent = @"
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=$mysqlPassword
DB_NAME=saista_bakers
DB_PORT=3306
FLASK_ENV=development
"@

$envContent | Out-File -Encoding UTF8 ".env"
Write-Host "✓ .env file created" -ForegroundColor Green

Write-Host ""

# Step 3: Setup Order Service
Write-Host "Step 3: Setting up Order Service (Flask)..." -ForegroundColor Yellow

$orderServicePath = Join-Path $projectRoot "order-service"
Set-Location $orderServicePath

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt -q
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Create .env file
$envContent = @"
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=$mysqlPassword
DB_NAME=saista_bakers
DB_PORT=3306
SMTP_SERVER=localhost
SMTP_PORT=1025
SENDER_EMAIL=noreply@saista-bakers.com
FLASK_ENV=development
"@

$envContent | Out-File -Encoding UTF8 ".env"
Write-Host "✓ .env file created" -ForegroundColor Green

Write-Host ""

# Step 4: Setup Frontend
Write-Host "Step 4: Setting up Frontend (React)..." -ForegroundColor Yellow

$frontendPath = Join-Path $projectRoot "frontend"
Set-Location $frontendPath

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies... (this may take a few minutes)"
    npm install --legacy-peer-deps
    Write-Host "✓ npm dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✓ npm dependencies already installed" -ForegroundColor Green
}

# Create .env file
$envContent = @"
REACT_APP_USER_SERVICE_URL=http://localhost:5001
REACT_APP_ORDER_SERVICE_URL=http://localhost:5002
"@

$envContent | Out-File -Encoding UTF8 ".env"
Write-Host "✓ .env file created" -ForegroundColor Green

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              Setup Complete! Ready to Start Services          ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Ensure MySQL is running:" -ForegroundColor White
Write-Host "   Start-Service MySQL80" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Open 3 new PowerShell windows and run each:" -ForegroundColor White
Write-Host ""
Write-Host "   Window 1 - User Service:" -ForegroundColor Cyan
Write-Host "   cd `$userServicePath" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python app/main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "   Window 2 - Order Service:" -ForegroundColor Cyan
Write-Host "   cd `$orderServicePath" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   python app/main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "   Window 3 - Frontend:" -ForegroundColor Cyan
Write-Host "   cd `$frontendPath" -ForegroundColor Gray
Write-Host "   npm start" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Visit http://localhost:3000 in your browser" -ForegroundColor White
Write-Host ""
Write-Host "4. Sign up and start testing!" -ForegroundColor White
Write-Host ""
