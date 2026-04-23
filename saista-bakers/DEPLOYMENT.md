# Deployment Guide

This guide covers deployment options for the Saista Bakers application.

## Table of Contents
1. [Docker Compose (Development/Small Production)](#docker-compose)
2. [Kubernetes Deployment](#kubernetes)
3. [Cloud Platforms](#cloud-platforms)
4. [Environment Configuration](#environment-configuration)

## Docker Compose

### Recommended For
- Local development
- Small production deployments
- Testing and staging

### Steps

1. **Prepare Production Compose File**
   ```bash
   cp docker-compose.yml docker-compose.prod.yml
   ```

2. **Update Configuration**
   - Change environment variables
   - Set strong JWT secret
   - Configure production SMTP server

3. **Deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Backup Database**
   ```bash
   docker exec saista-mysql mysqldump -u baker -pbaker123 saista_bakers > backup.sql
   ```

## Kubernetes

### Prerequisites
- kubectl installed
- Access to a Kubernetes cluster

### Deployment Steps

1. **Create namespace**
   ```bash
   kubectl create namespace saista-bakers
   ```

2. **Create secrets**
   ```bash
   kubectl create secret generic db-credentials \
     --from-literal=user=baker \
     --from-literal=password=baker123 \
     -n saista-bakers
   ```

3. **Deploy MySQL**
   ```bash
   kubectl apply -f k8s/mysql-deployment.yaml -n saista-bakers
   ```

4. **Deploy Services**
   ```bash
   kubectl apply -f k8s/user-service-deployment.yaml -n saista-bakers
   kubectl apply -f k8s/order-service-deployment.yaml -n saista-bakers
   kubectl apply -f k8s/frontend-deployment.yaml -n saista-bakers
   ```

5. **Check Status**
   ```bash
   kubectl get pods -n saista-bakers
   kubectl get services -n saista-bakers
   ```

## Cloud Platforms

### AWS Elastic Container Service (ECS)

1. **Push images to ECR**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker tag saista-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/saista-frontend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/saista-frontend:latest
   ```

2. **Create ECS cluster and task definitions**
3. **Configure RDS for MySQL**
4. **Update environment variables in task definitions**

### Google Cloud Run

1. **Deploy Frontend**
   ```bash
   gcloud run deploy saista-frontend --source . --region us-central1
   ```

2. **Deploy Services**
   ```bash
   gcloud run deploy saista-user-service --source user-service/ --region us-central1
   gcloud run deploy saista-order-service --source order-service/ --region us-central1
   ```

3. **Configure Cloud SQL for MySQL**

### Heroku

1. **Create Heroku apps**
   ```bash
   heroku create saista-frontend --buildpack heroku/nodejs
   heroku create saista-user-service --buildpack heroku/python
   heroku create saista-order-service --buildpack heroku/python
   ```

2. **Configure MySQL (use ClearDB add-on)**
   ```bash
   heroku addons:create cleardb:ignite -a saista-user-service
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

## Environment Configuration

### Production Environment Variables

**User Service (user-service/.env)**
```
DB_HOST=prod-mysql.example.com
DB_USER=secure_user
DB_PASSWORD=secure_password_here
DB_NAME=saista_bakers
DB_PORT=3306
FLASK_ENV=production
JWT_SECRET_KEY=your_very_secure_random_key_here_minimum_32_chars
```

**Order Service (order-service/.env)**
```
DB_HOST=prod-mysql.example.com
DB_USER=secure_user
DB_PASSWORD=secure_password_here
DB_NAME=saista_bakers
DB_PORT=3306
FLASK_ENV=production
JWT_SECRET_KEY=your_very_secure_random_key_here_minimum_32_chars
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=orders@saista-bakers.com
SENDER_PASSWORD=your_app_password_here
```

**Frontend (frontend/.env)**
```
REACT_APP_USER_SERVICE_URL=https://api.saista-bakers.com/user
REACT_APP_ORDER_SERVICE_URL=https://api.saista-bakers.com/order
```

### Generate Secure JWT Secret

```bash
# Linux/Mac
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Windows PowerShell
[System.Convert]::ToBase64String([System.Security.Cryptography.RNGCryptoServiceProvider]::new().GetBytes(32))
```

## SSL/TLS Configuration

### Using Let's Encrypt with Nginx

1. **Request Certificate**
   ```bash
   certbot certonly --standalone -d saista-bakers.com
   ```

2. **Update Nginx Configuration**
   ```nginx
   server {
       listen 443 ssl;
       server_name saista-bakers.com;
       
       ssl_certificate /etc/letsencrypt/live/saista-bakers.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/saista-bakers.com/privkey.pem;
       
       location / {
           proxy_pass http://frontend:3000;
       }
   }
   ```

## Scaling Considerations

### Database
- Use connection pooling
- Enable replication for high availability
- Consider read replicas for scaling

### Services
- Use load balancing (Nginx, HAProxy)
- Run multiple instances of each service
- Use auto-scaling based on CPU/memory

### Cache
- Add Redis for session management
- Cache product listings
- Cache user data

## Monitoring

### Key Metrics to Monitor
- API response times
- Database query performance
- Memory usage
- Error rates
- User authentication patterns

### Logging
- Configure centralized logging (ELK, Splunk)
- Log all API requests
- Log database errors
- Monitor SMTP failures

## Backup & Recovery

### MySQL Backup Strategy

**Daily Automatic Backup**
```bash
# Add to crontab
0 2 * * * mysqldump -u baker -pbaker123 saista_bakers | gzip > /backups/saista_bakers_$(date +%Y%m%d).sql.gz
```

**Restore from Backup**
```bash
mysql -u baker -pbaker123 saista_bakers < backup.sql
```

## Performance Optimization

1. **Enable GZIP compression**
   ```nginx
   gzip on;
   gzip_types text/plain application/json;
   ```

2. **Use CDN for static assets**
3. **Implement caching headers**
4. **Database indexing** (already configured in schema)
5. **API response optimization**

## Security Checklist

- [ ] Change JWT_SECRET_KEY
- [ ] Use HTTPS/SSL
- [ ] Enable CORS only for known domains
- [ ] Implement rate limiting
- [ ] Use strong database passwords
- [ ] Enable database backups
- [ ] Configure firewall rules
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS for all API calls
- [ ] Implement API key management
- [ ] Set up monitoring and alerts
- [ ] Regular security audits
- [ ] Use Web Application Firewall (WAF)

## Rollback Procedure

If deployment fails:

1. **Revert to previous Docker images**
   ```bash
   docker pull previous-image-tag
   docker-compose up -d
   ```

2. **Restore database from backup**
   ```bash
   mysql saista_bakers < backup.sql
   ```

3. **Check service status**
   ```bash
   docker-compose ps
   ```

## Support & Maintenance

- Monitor error logs regularly
- Keep dependencies updated
- Schedule regular backups
- Perform security updates promptly
- Test disaster recovery procedures

For more information, refer to the main README.md file.
