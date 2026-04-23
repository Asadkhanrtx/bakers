# Local Development Setup Guide (Without Docker)

This guide provides step-by-step instructions to run the Saista Bakers application on localhost.

## Prerequisites

Make sure you have installed:

1. **MySQL 8.0+**
   - Download from: https://dev.mysql.com/downloads/mysql/
   - Or use: `choco install mysql` (Windows) or `brew install mysql` (Mac)

2. **Python 3.9+**
   - Download from: https://www.python.org/downloads/
   - Or use: `choco install python` (Windows) or `brew install python` (Mac)

3. **Node.js 14+**
   - Download from: https://nodejs.org/
   - Or use: `choco install nodejs` (Windows) or `brew install node` (Mac)

---

## Step 1: Setup MySQL Database

### Windows PowerShell

1. **Start MySQL service:**
   ```powershell
   # If MySQL is installed as a service
   Start-Service MySQL80
   # Or Start-Service MySQL57 depending on your version
   ```

2. **Access MySQL:**
   ```powershell
   mysql -u root -p
   # Enter your MySQL root password (default is usually blank, just press Enter)
   ```

3. **Create database and import schema:**
   ```bash
   # From PowerShell, navigate to project folder
   cd c:\Users\307417\Desktop\bakers\saista-bakers
   
   # Import the schema
   mysql -u root -p < database/schema.sql
   ```

4. **Verify database:**
   ```sql
   mysql -u root -p
   ```
   Then run:
   ```sql
   USE saista_bakers;
   SHOW TABLES;
   SELECT * FROM products;
   ```

### Mac/Linux

```bash
# Install MySQL if not present
brew install mysql

# Start MySQL
brew services start mysql

# Access MySQL
mysql -u root

# Import schema
mysql -u root < database/schema.sql

# Verify
mysql -u root -e "USE saista_bakers; SHOW TABLES;"
```

---

## Step 2: Setup User Service (Flask)

### Windows PowerShell

1. **Navigate to user-service:**
   ```powershell
   cd c:\Users\307417\Desktop\bakers\saista-bakers\user-service
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   If you get execution policy error:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Create .env file:**
   ```powershell
   @"
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=
   DB_NAME=saista_bakers
   DB_PORT=3306
   FLASK_ENV=development
   "@ | Out-File -Encoding UTF8 .env
   ```

6. **Run the service:**
   ```powershell
   python app/app.py
   ```

   You should see: `Running on http://0.0.0.0:5001/`

### Mac/Linux

```bash
# Navigate to user-service
cd ~/path/to/saista-bakers/user-service

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=saista_bakers
DB_PORT=3306
FLASK_ENV=development
EOF

# Run the service
python app/app.py
```

---

## Step 3: Setup Order Service (Flask)

### Windows PowerShell

Open a **NEW PowerShell window**:

1. **Navigate to order-service:**
   ```powershell
   cd c:\Users\307417\Desktop\bakers\saista-bakers\order-service
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv venv
   ```

3. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Create .env file:**
   ```powershell
   @"
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=
   DB_NAME=saista_bakers
   DB_PORT=3306
   SMTP_SERVER=localhost
   SMTP_PORT=1025
   SENDER_EMAIL=noreply@saista-bakers.com
   FLASK_ENV=development
   "@ | Out-File -Encoding UTF8 .env
   ```

6. **Run the service:**
   ```powershell
   python app/app.py
   ```

   You should see: `Running on http://0.0.0.0:5002/`

### Mac/Linux

```bash
# Navigate to order-service
cd ~/path/to/saista-bakers/order-service

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=saista_bakers
DB_PORT=3306
SMTP_SERVER=localhost
SMTP_PORT=1025
SENDER_EMAIL=noreply@saista-bakers.com
FLASK_ENV=development
EOF

# Run the service
python app/app.py
```

---

## Step 4: Setup Frontend (React)

### Windows PowerShell

Open a **NEW PowerShell window**:

1. **Navigate to frontend:**
   ```powershell
   cd c:\Users\307417\Desktop\bakers\saista-bakers\frontend
   ```

2. **Install dependencies:**
   ```powershell
   npm install
   ```

3. **Create .env file:**
   ```powershell
   @"
   REACT_APP_USER_SERVICE_URL=http://localhost:5001
   REACT_APP_ORDER_SERVICE_URL=http://localhost:5002
   "@ | Out-File -Encoding UTF8 .env
   ```

4. **Start development server:**
   ```powershell
   npm start
   ```

   Browser will automatically open to: `http://localhost:3000`

### Mac/Linux

```bash
# Navigate to frontend
cd ~/path/to/saista-bakers/frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
REACT_APP_USER_SERVICE_URL=http://localhost:5001
REACT_APP_ORDER_SERVICE_URL=http://localhost:5002
EOF

# Start development server
npm start
```

---

## Summary: Services Running

You should have 4 terminal windows open:

| Window | Service | Port | Command |
|--------|---------|------|---------|
| 1 | MySQL Database | 3306 | (running in background) |
| 2 | User Service | 5001 | `python app/app.py` |
| 3 | Order Service | 5002 | `python app/app.py` |
| 4 | Frontend | 3000 | `npm start` |

---

## Access Points

- **Frontend:** http://localhost:3000
- **User Service API:** http://localhost:5001
- **Order Service API:** http://localhost:5002
- **MySQL:** localhost:3306 (user: root)

---

## Troubleshooting

### MySQL Connection Error

**Error:** `Can't connect to MySQL server on 'localhost'`

**Solution:**
```powershell
# Check if MySQL is running
Get-Service MySQL80

# Start MySQL service
Start-Service MySQL80

# Or verify MySQL is installed
mysql --version
```

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```powershell
# Find process using port 5001
Get-NetTCPConnection -LocalPort 5001

# Kill the process
Stop-Process -Id <PID> -Force

# Alternative: Change port in app.py
# app.run(port=5003)
```

### Python Virtual Environment Issues

**Error:** `'python' is not recognized`

**Solution:**
```powershell
# Use full path to Python
C:\Users\307417\AppData\Local\Programs\Python\Python39\python.exe -m venv venv

# Add Python to PATH
$env:Path += ";C:\Users\307417\AppData\Local\Programs\Python\Python39"
```

### npm install fails

**Error:** `npm: command not found`

**Solution:**
```powershell
# Reinstall Node.js from https://nodejs.org/
# Or use Chocolatey
choco install nodejs

# Verify installation
node --version
npm --version
```

### Frontend can't connect to API

**Error:** CORS error or 404 in browser console

**Solution:**
1. Ensure both Flask services are running
2. Check .env file in frontend folder has correct URLs
3. Restart frontend: `npm start`
4. Check browser console (F12) for exact error

### Database password issues

**If you set a MySQL password:**

Update .env files in both services:
```
DB_PASSWORD=your_password_here
```

---

## Development Workflow

1. **Make changes to code**
2. **Services auto-reload** (Flask in debug mode, React with hot reload)
3. **Refresh browser** if needed
4. **Check terminal for errors**

### Stopping All Services

```powershell
# In each terminal window, press: Ctrl + C

# Stop MySQL service
Stop-Service MySQL80
```

---

## Database Management

### View Database

```powershell
# Connect to MySQL
mysql -u root -p

# Use database
USE saista_bakers;

# View tables
SHOW TABLES;

# View specific table
SELECT * FROM products;
SELECT * FROM users;
SELECT * FROM orders;
```

### Reset Database

```powershell
# Drop and recreate
mysql -u root -p < database/schema.sql
```

### Backup Database

```powershell
# Create backup
mysqldump -u root -p saista_bakers > backup.sql

# Restore from backup
mysql -u root -p saista_bakers < backup.sql
```

---

## Testing the Application

1. **Open http://localhost:3000**
2. **Sign Up** with test credentials
3. **Browse Products** - You should see 6 sample products
4. **Add to Cart** - Select products
5. **Checkout** - Place order
6. **View Orders** - See order history
7. **Custom Cake** - Design custom cake and see pricing

---

## Useful Commands

### Check if ports are available
```powershell
netstat -ano | findstr :3000
netstat -ano | findstr :5001
netstat -ano | findstr :5002
netstat -ano | findstr :3306
```

### View Flask logs
```powershell
# Logs appear in the terminal where Flask is running
# Enable more verbose logging by modifying app.py:
# app.run(debug=True, host='0.0.0.0', port=5001)
```

### View npm logs
```powershell
# Check terminal where `npm start` is running
# Clear: npm cache clean --force
```

---

## Performance Tips

- Use `npm run build` and serve with a production server for testing
- Enable MySQL query logs to debug slow queries
- Use browser DevTools (F12) to debug frontend issues

---

## Next Steps

- Refer to README.md for API documentation
- Check DEPLOYMENT.md for production setup
- Modify products in database/schema.sql for custom products
- Customize Flask app configuration in app.py files

---

**You're all set! Happy development! 🎂**
