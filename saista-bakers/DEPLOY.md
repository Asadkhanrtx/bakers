# AWS Deployment Guide

This guide explains exactly how to deploy the Saista Bakers application on your AWS Ubuntu instance using Docker and Docker Compose.

## Prerequisites on AWS

1. Connect to your AWS Ubuntu instance via SSH.
2. Install Docker and Docker Compose if you haven't already:
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose -y
   sudo systemctl enable docker
   sudo systemctl start docker
   sudo usermod -aG docker ubuntu
   ```
   *(Note: You might need to log out and log back in for the docker group to take effect)*

## Deployment Steps

### 1. Clone the Repository
Clone the code directly onto your AWS instance:
```bash
git clone https://github.com/Asadkhanrtx/bakers.git
cd bakers/saista-bakers
```

### 2. Build and Start the Containers
Since everything is now configured for production (using Nginx as a reverse proxy), you simply need to run:
```bash
docker-compose up -d --build
```
This command will:
- Build the `asadoblivion/saista-...` Docker images.
- Start the MySQL database and MailHog.
- Start the Python backend microservices (completely hidden from the public internet).
- Start the Nginx frontend on **Port 80**.

### 3. Initialize the Database
Since the MySQL container is fresh on AWS, you need to create the tables and the initial admin user. Run the migration script inside the running user-service container:
```bash
docker exec -it saista-user-service python /app/migrate_db.py
```

### 4. Open Port 80 in AWS
Go to your AWS EC2 Console -> Security Groups.
Edit Inbound Rules and ensure **Port 80 (HTTP)** is open to `0.0.0.0/0` (Anywhere).

## You're Done!
You can now visit your application by typing the AWS instance's Public IP address into your browser:
`http://<YOUR_AWS_PUBLIC_IP>`

The Frontend will load automatically. All API requests (like logging in, ordering) will securely route through Nginx to the internal Docker containers. 

### Admin Login
- URL: `http://<YOUR_AWS_PUBLIC_IP>/admin/login`
- Username: `admin`
- Password: `Admin@1234`
