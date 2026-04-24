@echo off
echo Starting Saista Bakers Services...

start "User Service" cmd /k "cd /d %~dp0user-service && python -m uvicorn app.main:app --host 0.0.0.0 --port 5001"
timeout /t 2 >nul

start "Order Service" cmd /k "cd /d %~dp0order-service && python -m uvicorn app.main:app --host 0.0.0.0 --port 5002"
timeout /t 2 >nul

start "Payment Service" cmd /k "cd /d %~dp0payment-service && python -m uvicorn app.main:app --host 0.0.0.0 --port 5003"
timeout /t 2 >nul

echo All backend services started in separate windows!
pause
