# Prerequisites Installation Guide

## Quick Install with Chocolatey (Recommended)

### Step 1: Install Chocolatey

Run PowerShell as Administrator and execute:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### Step 2: Install Python, Node.js, and MySQL

```powershell
# Run as Administrator
choco install python nodejs mysql -y
```

### Step 3: Restart PowerShell

Close PowerShell and open a new one for changes to take effect.

### Step 4: Verify Installations

```powershell
python --version
node --version
npm --version
mysql --version
```

---

## Manual Installation (If Chocolatey doesn't work)

### Install Python
1. Download from: https://www.python.org/downloads/
2. Run installer
3. ✅ Check "Add Python to PATH" during installation
4. Restart PowerShell

### Install Node.js
1. Download from: https://nodejs.org/ (LTS version recommended)
2. Run installer
3. Follow default installation steps
4. Restart PowerShell

### Install MySQL
1. Download from: https://dev.mysql.com/downloads/mysql/
2. Run MySQL installer
3. Choose "Standard Configuration"
4. Remember the password you set for root user

---

## After Installation

Once all tools are installed and you've restarted PowerShell:

```powershell
cd c:\Users\307417\Desktop\bakers\saista-bakers
```

Then follow the Automated Installation Guide in AUTOMATED_INSTALL.md

---

**Make sure all prerequisites show correct versions before proceeding!**
