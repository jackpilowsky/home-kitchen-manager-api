# Docker Setup Guide

## Overview

This guide covers the complete Docker setup for the Home Kitchen Manager API, including development and production configurations.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git

## Quick Start

### Development Environment

1. **Clone and setup**:
```bash
git clone <repository-url>
cd home-kitchen-manager-api
cp .env.example .env
```

2. **Start development environment**:
```bash
docker-compose -f docker-compose.dev.yml up -d
```

3. **Run database migrations**:
```bash
docker-compose -f docker-compose.dev.yml exec api alembic upgrade head
```

4. **Access the application**:
- API: http://localhost:8001
- Documentation: http://localhost:8001/docs
- Database: localhost:5433 (postgres/postgres)
- Redis: localhost:6380

### Production Environment

1. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with production values
```

2. **Start production environment**:
```bash
docker-compose up -d
```

3. **Run database migrations**:
```bash
docker-compose exec api alembic upgrade head
```

4. **Access the application**:
- API: http://localhost (via Nginx)
- Documentation: http://localhost/docs
- Health Check: http://localhost/health

## Docker Configuration

### Services Overview

#### Development (`docker-compose.dev.yml`)
- **api**: FastAPI application with hot reload
- **db**: PostgreSQL 15 database
- **redis**: Redis cache

#### Production (`docker-compose.yml`)
- **api**: FastAPI application (production build)
- **db**: PostgreSQL 15 database with persistence
- **redis**: Redis cache with persistence
- **nginx**: Reverse proxy with rate limiting

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database Configuration
DATABASE_NAME=kitchen_manager
DATABASE_USER=postgres
DATABASE_PASSWORD=your_secure_password
DATABASE_HOST=db
DATABASE_PORT=5432

# Redis Configuration
REDIS_URL=redis://redis:6379

# Application Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production

# Security
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
CORS_ORIGINS=http://localhost:3000,https://your-frontend.com
```

## Docker Commands

### Development Commands

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f api

# Execute commands in container
docker-compose -f docker-compose.dev.yml exec api bash

# Run database migrations
docker-compose -f docker-compose.dev.yml exec api alembic upgrade head

# Create new migration
docker-compose -f docker-compose.dev.yml exec api alembic revision -m "Description"

# Run tests
docker-compose -f docker-compose.dev.yml exec api pytest

# Stop development environment
docker-compose -f docker-compose.dev.yml down
```

### Production Commands

```bash
# Start production environment
docker-compose up -d

# View logs
docker-compose logs -f

# Execute commands in container
docker-compose exec api bash

# Run database migrations
docker-compose exec api alembic upgrade head

# Backup database
docker-compose exec db pg_dump -U postgres kitchen_manager > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres kitchen_manager < backup.sql

# Stop production environment
docker-compose down
```

### Maintenance Commands

```bash
# Update containers
docker-compose pull
docker-compose up -d

# Clean up unused resources
docker system prune -f

# View container resource usage
docker stats

# Inspect container
docker-compose exec api ps aux
docker-compose exec api df -h
```

## File Structure

```
.
├── Dockerfile                 # Production Dockerfile
├── Dockerfile.dev            # Development Dockerfile
├── docker-compose.yml        # Production compose file
├── docker-compose.dev.yml    # Development compose file
├── .dockerignore             # Docker ignore file
├── nginx.conf                # Nginx configuration
├── init-db.sql              # Database initialization
└── requirements.txt          # Python dependencies
```

## Container Details

### API Container (FastAPI)

**Production Build:**
- Base: `python:3.11-slim`
- User: Non-root `app` user
- Port: 8000
- Health check: `/api/v1/health`
- Restart policy: `unless-stopped`

**Development Build:**
- Hot reload enabled
- Volume mounting for code changes
- Debug mode enabled

### Database Container (PostgreSQL)

**Configuration:**
- Version: PostgreSQL 15 Alpine
- Port: 5432 (internal), 5432/5433 (external)
- Persistent storage: Docker volume
- Health check: `pg_isready`
- Extensions: `uuid-ossp`, `pg_trgm`

**Backup Strategy:**
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec db pg_dump -U postgres kitchen_manager > "backup_${DATE}.sql"
```

### Redis Container

**Configuration:**
- Version: Redis 7 Alpine
- Port: 6379 (internal), 6379/6380 (external)
- Persistent storage: Docker volume
- Health check: `redis-cli ping`

### Nginx Container (Production Only)

**Features:**
- Reverse proxy to API
- Rate limiting (10 req/s, burst 20)
- Security headers
- CORS handling
- Static file serving
- SSL/TLS ready

**Configuration:**
```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

# Security headers
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
```

## Networking

### Development Network
- Network: `kitchen_dev_network`
- Driver: Bridge
- Internal communication between containers

### Production Network
- Network: `kitchen_network`
- Driver: Bridge
- Nginx as entry point
- Internal service communication

## Volumes

### Persistent Data
- `postgres_data`: Database files
- `redis_data`: Redis persistence
- `./logs`: Application logs (mounted)

### Development Volumes
- `.:/app`: Code hot reload
- `/app/__pycache__`: Exclude cache

## Health Checks

### API Health Check
```bash
curl -f http://localhost:8000/api/v1/health || exit 1
```

### Database Health Check
```bash
pg_isready -U postgres
```

### Redis Health Check
```bash
redis-cli ping
```

## Monitoring

### Container Monitoring
```bash
# Resource usage
docker stats

# Container logs
docker-compose logs -f --tail=100

# Health status
docker-compose ps
```

### Application Monitoring
- Health endpoint: `/api/v1/health`
- Metrics endpoint: `/api/v1/dashboard/metrics`
- Detailed health: `/api/v1/health/detailed`

## Security Considerations

### Container Security
- Non-root user in containers
- Minimal base images (Alpine/Slim)
- No unnecessary packages
- Regular security updates

### Network Security
- Internal network isolation
- Rate limiting via Nginx
- CORS configuration
- Security headers

### Data Security
- Environment variable secrets
- Database password protection
- JWT token security
- Input validation

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check logs
docker-compose logs api

# Check container status
docker-compose ps

# Restart specific service
docker-compose restart api
```

**Database connection issues:**
```bash
# Check database status
docker-compose exec db pg_isready -U postgres

# Check network connectivity
docker-compose exec api ping db

# Verify environment variables
docker-compose exec api env | grep DATABASE
```

**Permission issues:**
```bash
# Check file permissions
ls -la

# Fix ownership (if needed)
sudo chown -R $USER:$USER .
```

### Performance Optimization

**Database Performance:**
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

**Container Resources:**
```yaml
# Add resource limits
services:
  api:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

## Deployment

### CI/CD Pipeline Example

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and deploy
        run: |
          docker-compose build
          docker-compose up -d
          docker-compose exec api alembic upgrade head
```

### Production Deployment Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database backups configured
- [ ] Monitoring setup
- [ ] Log rotation configured
- [ ] Security headers enabled
- [ ] Rate limiting configured
- [ ] Health checks working

## Backup and Recovery

### Database Backup
```bash
# Create backup
docker-compose exec db pg_dump -U postgres kitchen_manager > backup.sql

# Restore backup
docker-compose exec -T db psql -U postgres kitchen_manager < backup.sql
```

### Full System Backup
```bash
# Backup volumes
docker run --rm -v kitchen_manager_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore volumes
docker run --rm -v kitchen_manager_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

## Support

For Docker-related issues:
- Check container logs: `docker-compose logs`
- Verify configuration: `docker-compose config`
- Monitor resources: `docker stats`
- Health checks: `docker-compose ps`