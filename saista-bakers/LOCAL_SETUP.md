# Saista Bakers - Local Setup Guide

Welcome to the Saista Bakers project! This guide will help you set up and run the fully decoupled microservices architecture locally.

## Prerequisites

1. **Docker & Docker Compose**: Ensure Docker Desktop is installed and running.
2. **Node.js (18+)**: For running the frontend locally if not using Docker for frontend development.
3. **Python (3.9+)**: For running backend services locally if not using Docker.

## Running with Docker Compose (Recommended)

This is the easiest way to get everything up and running, including the MySQL database, MailHog (for SMTP), and all microservices.

```bash
# 1. Start all services in detached mode
docker-compose up -d --build

# 2. Check the status of the containers
docker-compose ps
```

The services will be available at:
- **Frontend**: http://localhost:3000
- **User Service (API)**: http://localhost:5001
- **Order Service (API)**: http://localhost:5002
- **Payment Service (API)**: http://localhost:5003
- **MailHog (Web UI for dummy emails)**: http://localhost:8025

### Database Migrations & Initial Data
The database schema will be automatically created on the first run via `database/schema.sql`.

To initialize the `admin` user, you can run the migration script inside the `user-service`:
```bash
docker exec -it saista-user-service python /app/migrate_db.py
```
*Note: Make sure to copy the `migrate_db.py` to the `user-service/app` folder before building, or run the equivalent queries directly in the DB.*

Default Admin Login:
- Username: `admin`
- Password: `Admin@1234`

## Stopping the Services

```bash
docker-compose down
```

---

## Developing Locally Without Docker (Backend)

If you prefer running the Python services directly on your machine for debugging:

### 1. Start Database & MailHog only
```bash
docker-compose up -d mysql mailhog
```

### 2. Install Dependencies & Run User Service
```bash
cd user-service
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 5001 --reload
```

### 3. Install Dependencies & Run Order Service
```bash
cd order-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 5002 --reload
```

### 4. Install Dependencies & Run Payment Service
```bash
cd payment-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 5003 --reload
```

### 5. Run Frontend
```bash
cd frontend
npm install
npm start
```
