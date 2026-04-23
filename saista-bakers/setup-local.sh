#!/bin/bash

# Saista Bakers - Local Setup Script for Mac/Linux
# Usage: bash setup-local.sh

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          Saista Bakers - Local Development Setup             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found. Install with: brew install python (Mac) or apt-get install python3 (Linux)"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✓ $PYTHON_VERSION"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "✗ Node.js not found. Install with: brew install node (Mac) or apt-get install nodejs (Linux)"
    exit 1
fi
NODE_VERSION=$(node --version)
echo "✓ Node.js: $NODE_VERSION"

# Check MySQL
if ! command -v mysql &> /dev/null; then
    echo "✗ MySQL not found. Install with: brew install mysql (Mac) or apt-get install mysql-server (Linux)"
    exit 1
fi
echo "✓ MySQL found"

echo ""
echo "All prerequisites found!"
echo ""

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Step 1: Setup MySQL Database
echo "Step 1: Setting up MySQL database..."
read -sp "Enter your MySQL root password (press Enter if no password): " MYSQL_PASSWORD
echo ""

if [ -z "$MYSQL_PASSWORD" ]; then
    mysql -u root < "$PROJECT_ROOT/database/schema.sql" 2>/dev/null
else
    mysql -u root -p"$MYSQL_PASSWORD" < "$PROJECT_ROOT/database/schema.sql" 2>/dev/null
fi

if [ $? -eq 0 ]; then
    echo "✓ Database schema imported"
else
    echo "⚠ Could not import database automatically"
    echo "  Run manually: mysql -u root -p < database/schema.sql"
fi

echo ""

# Step 2: Setup User Service
echo "Step 2: Setting up User Service (Flask)..."

USER_SERVICE_PATH="$PROJECT_ROOT/user-service"
cd "$USER_SERVICE_PATH"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

# Create .env file
cat > .env << EOF
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=$MYSQL_PASSWORD
DB_NAME=saista_bakers
DB_PORT=3306
FLASK_ENV=development
EOF

echo "✓ .env file created"

echo ""

# Step 3: Setup Order Service
echo "Step 3: Setting up Order Service (Flask)..."

ORDER_SERVICE_PATH="$PROJECT_ROOT/order-service"
cd "$ORDER_SERVICE_PATH"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

# Create .env file
cat > .env << EOF
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=$MYSQL_PASSWORD
DB_NAME=saista_bakers
DB_PORT=3306
SMTP_SERVER=localhost
SMTP_PORT=1025
SENDER_EMAIL=noreply@saista-bakers.com
FLASK_ENV=development
EOF

echo "✓ .env file created"

echo ""

# Step 4: Setup Frontend
echo "Step 4: Setting up Frontend (React)..."

FRONTEND_PATH="$PROJECT_ROOT/frontend"
cd "$FRONTEND_PATH"

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies... (this may take a few minutes)"
    npm install --legacy-peer-deps
    echo "✓ npm dependencies installed"
else
    echo "✓ npm dependencies already installed"
fi

# Create .env file
cat > .env << EOF
REACT_APP_USER_SERVICE_URL=http://localhost:5001
REACT_APP_ORDER_SERVICE_URL=http://localhost:5002
EOF

echo "✓ .env file created"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              Setup Complete! Ready to Start Services          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next Steps:"
echo ""
echo "1. Start MySQL (if not already running):"
echo "   brew services start mysql  # Mac"
echo "   sudo service mysql start   # Linux"
echo ""
echo "2. Open 3 new terminal windows and run each:"
echo ""
echo "   Terminal 1 - User Service:"
echo "   cd $USER_SERVICE_PATH"
echo "   source venv/bin/activate"
echo "   python app/app.py"
echo ""
echo "   Terminal 2 - Order Service:"
echo "   cd $ORDER_SERVICE_PATH"
echo "   source venv/bin/activate"
echo "   python app/app.py"
echo ""
echo "   Terminal 3 - Frontend:"
echo "   cd $FRONTEND_PATH"
echo "   npm start"
echo ""
echo "3. Visit http://localhost:3000 in your browser"
echo ""
echo "4. Sign up and start testing!"
echo ""
