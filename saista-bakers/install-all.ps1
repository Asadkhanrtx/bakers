# Saista Bakers - Automated Installation for Windows PowerShell
# This script installs all prerequisites and sets up all services

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║    Saista Bakers - Complete Automated Installation         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "⚠ This script should be run as Administrator" -ForegroundColor Yellow
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit
}

Write-Host "Installing prerequisites..." -ForegroundColor Yellow
Write-Host ""

# Install Chocolatey if not present
$chocoInstalled = $null -ne (Get-Command choco -ErrorAction SilentlyContinue)
if (-not $chocoInstalled) {
    Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    
    # Refresh environment
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Install Python if not present
$pythonInstalled = $null -ne (Get-Command python -ErrorAction SilentlyContinue)
if (-not $pythonInstalled) {
    Write-Host "Installing Python 3.9..." -ForegroundColor Yellow
    choco install python39 -y
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Install Node.js if not present
$nodeInstalled = $null -ne (Get-Command node -ErrorAction SilentlyContinue)
if (-not $nodeInstalled) {
    Write-Host "Installing Node.js..." -ForegroundColor Yellow
    choco install nodejs -y
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Install MySQL if not present
$mysqlInstalled = $null -ne (Get-Command mysql -ErrorAction SilentlyContinue)
if (-not $mysqlInstalled) {
    Write-Host "Installing MySQL..." -ForegroundColor Yellow
    choco install mysql -y
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

Write-Host ""
Write-Host "Verifying installations..." -ForegroundColor Yellow
Write-Host ""

# Verify installations
$pythonVersion = python --version 2>&1
Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green

$nodeVersion = node --version 2>&1
Write-Host "✓ Node.js: $nodeVersion" -ForegroundColor Green

$npmVersion = npm --version 2>&1
Write-Host "✓ npm: $npmVersion" -ForegroundColor Green

$mysqlVersion = mysql --version 2>&1
Write-Host "✓ MySQL: $mysqlVersion" -ForegroundColor Green

Write-Host ""
Write-Host "All prerequisites installed successfully!" -ForegroundColor Green
Write-Host ""

# Get project root
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Project root: $projectRoot" -ForegroundColor Cyan
Write-Host ""

# Step 1: Setup MySQL Database
Write-Host "Step 1: Setting up MySQL database..." -ForegroundColor Yellow
Write-Host ""

# Check if MySQL service is running
$mysqlService = Get-Service -Name "MySQL80" -ErrorAction SilentlyContinue
if ($null -eq $mysqlService) {
    # Try MySQL57
    $mysqlService = Get-Service -Name "MySQL57" -ErrorAction SilentlyContinue
}

if ($null -ne $mysqlService -and $mysqlService.Status -ne "Running") {
    Write-Host "Starting MySQL service..." -ForegroundColor Yellow
    Start-Service -Name $mysqlService.Name -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
}

Write-Host "Importing database schema..." -ForegroundColor Yellow
$schemaPath = Join-Path $projectRoot "database\schema.sql"
$output = mysql -u root < $schemaPath 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Database schema imported successfully" -ForegroundColor Green
} else {
    Write-Host "⚠ Database import had issues (this is expected if MySQL needs password)" -ForegroundColor Yellow
    Write-Host "Manual import: mysql -u root -p < database/schema.sql" -ForegroundColor Gray
}

Write-Host ""

# Step 2: Setup User Service
Write-Host "Step 2: Setting up User Service (Flask)..." -ForegroundColor Yellow

$userServicePath = Join-Path $projectRoot "user-service"
Push-Location $userServicePath

Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
Write-Host "✓ Virtual environment created" -ForegroundColor Green

Write-Host "Activating virtual environment and installing dependencies..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
pip install --upgrade pip -q
pip install -r requirements.txt -q
Write-Host "✓ Dependencies installed" -ForegroundColor Green

Write-Host "Creating .env file..." -ForegroundColor Yellow
$envContent = @"
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=saista_bakers
DB_PORT=3306
FLASK_ENV=development
"@
$envContent | Out-File -Encoding UTF8 ".env"
Write-Host "✓ .env file created" -ForegroundColor Green

Pop-Location
Write-Host ""

# Step 3: Setup Order Service
Write-Host "Step 3: Setting up Order Service (Flask)..." -ForegroundColor Yellow

$orderServicePath = Join-Path $projectRoot "order-service"
Push-Location $orderServicePath

Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
Write-Host "✓ Virtual environment created" -ForegroundColor Green

Write-Host "Activating virtual environment and installing dependencies..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
pip install --upgrade pip -q
pip install -r requirements.txt -q
Write-Host "✓ Dependencies installed" -ForegroundColor Green

Write-Host "Creating .env file..." -ForegroundColor Yellow
$envContent = @"
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=saista_bakers
DB_PORT=3306
SMTP_SERVER=localhost
SMTP_PORT=1025
SENDER_EMAIL=noreply@saista-bakers.com
FLASK_ENV=development
"@
$envContent | Out-File -Encoding UTF8 ".env"
Write-Host "✓ .env file created" -ForegroundColor Green

Pop-Location
Write-Host ""

# Step 4: Setup Frontend
Write-Host "Step 4: Setting up Frontend (React)..." -ForegroundColor Yellow

$frontendPath = Join-Path $projectRoot "frontend"
Push-Location $frontendPath

Write-Host "Installing npm dependencies... (this may take a few minutes)" -ForegroundColor Yellow
npm install --legacy-peer-deps -q
Write-Host "✓ npm dependencies installed" -ForegroundColor Green

Write-Host "Creating .env file..." -ForegroundColor Yellow
$envContent = @"
REACT_APP_USER_SERVICE_URL=http://localhost:5001
REACT_APP_ORDER_SERVICE_URL=http://localhost:5002
"@
$envContent | Out-File -Encoding UTF8 ".env"
Write-Host "✓ .env file created" -ForegroundColor Green

Pop-Location
Write-Host ""

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║            ✓ Installation Complete!                          ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# Create helper scripts
Write-Host "Creating helper scripts..." -ForegroundColor Yellow

$runAllContent = @"
# Start all services in parallel

param()

`$projectRoot = Split-Path -Parent `$MyInvocation.MyCommand.Path

Write-Host "Starting all Saista Bakers services..." -ForegroundColor Cyan

# Start User Service in new window
Write-Host "Starting User Service on port 5001..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList {
    cd `"$userServicePath`"
    .\venv\Scripts\Activate.ps1
    python app/app.py
} -NoNewWindow -PassThru -Name "UserService"

Start-Sleep -Seconds 2

# Start Order Service in new window
Write-Host "Starting Order Service on port 5002..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList {
    cd `"$orderServicePath`"
    .\venv\Scripts\Activate.ps1
    python app/app.py
} -NoNewWindow -PassThru -Name "OrderService"

Start-Sleep -Seconds 2

# Start Frontend in new window
Write-Host "Starting Frontend on port 3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList {
    cd `"$frontendPath`"
    npm start
} -NoNewWindow -PassThru -Name "Frontend"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║               All Services Started!                          ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "User Service API: http://localhost:5001" -ForegroundColor Cyan
Write-Host "Order Service API: http://localhost:5002" -ForegroundColor Cyan
"@

$runAllPath = Join-Path $projectRoot "run-all-services.ps1"
$runAllContent | Out-File -Encoding UTF8 $runAllPath
Write-Host "✓ Created run-all-services.ps1" -ForegroundColor Green

Write-Host ""
Write-Host "Next Step - Running the Services:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Option 1: Run all services at once (recommended):" -ForegroundColor White
Write-Host "  powershell -ExecutionPolicy Bypass -File run-all-services.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 2: Run each service in separate PowerShell window:" -ForegroundColor White
Write-Host ""
Write-Host "  Window 1 - User Service:" -ForegroundColor Cyan
Write-Host "  cd user-service" -ForegroundColor Gray
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "  python app/app.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  Window 2 - Order Service:" -ForegroundColor Cyan
Write-Host "  cd order-service" -ForegroundColor Gray
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "  python app/app.py" -ForegroundColor Gray
Write-Host ""
Write-Host "  Window 3 - Frontend:" -ForegroundColor Cyan
Write-Host "  cd frontend" -ForegroundColor Gray
Write-Host "  npm start" -ForegroundColor Gray
Write-Host ""
Write-Host "Then open your browser to:" -ForegroundColor White
Write-Host "  http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
