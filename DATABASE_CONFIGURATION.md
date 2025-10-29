# Database Configuration Guide - AWS RDS PostgreSQL

## Overview

This guide covers the comprehensive database configuration for the Home Kitchen Manager API, optimized for PostgreSQL running on AWS RDS with advanced connection pooling, monitoring, and performance optimization.

## Configuration Architecture

### Connection Pool Settings

The application uses SQLAlchemy's QueuePool with the following optimized settings for AWS RDS:

```python
# Production Settings
DB_POOL_SIZE=20              # Base connection pool size
DB_MAX_OVERFLOW=30           # Additional connections beyond pool_size
DB_POOL_TIMEOUT=30           # Seconds to wait for connection
DB_POOL_RECYCLE=3600         # Recycle connections every hour
DB_POOL_PRE_PING=true        # Validate connections before use
```

### AWS RDS Specific Configuration

```bash
# Connection Settings
DB_CONNECT_TIMEOUT=10        # Connection timeout in seconds
DB_READ_TIMEOUT=30           # Read timeout in seconds
DB_SSL_MODE=require          # Force SSL connections
DB_APPLICATION_NAME=kitchen_manager_api  # Application identifier

# Performance Settings
DB_STATEMENT_TIMEOUT=30000   # 30 seconds statement timeout
DB_IDLE_TIMEOUT=300000       # 5 minutes idle transaction timeout
```

## Environment Configuration

### Production Environment (.env)

```bash
# AWS RDS PostgreSQL Configuration
DATABASE_URL=postgresql://username:password@your-rds-endpoint.region.rds.amazonaws.com:5432/kitchen_manager
DATABASE_HOST=your-rds-endpoint.region.rds.amazonaws.com
DATABASE_PORT=5432
DATABASE_NAME=kitchen_manager
DATABASE_USER=your_db_username
DATABASE_PASSWORD=your_secure_db_password

# Connection Pool (Production Optimized)
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=true

# AWS RDS Settings
DB_CONNECT_TIMEOUT=10
DB_READ_TIMEOUT=30
DB_SSL_MODE=require
DB_APPLICATION_NAME=kitchen_manager_api
DB_STATEMENT_TIMEOUT=30000
DB_IDLE_TIMEOUT=300000
```

### Development Environment

```bash
# Local PostgreSQL for Development
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/kitchen_manager_dev
DB_POOL_SIZE=5               # Smaller pool for development
DB_MAX_OVERFLOW=10
DB_SSL_MODE=disable          # No SSL for local development
```

## AWS RDS Setup

### 1. RDS Instance Configuration

**Recommended Instance Settings:**
- **Instance Class**: db.t3.medium (minimum for production)
- **Engine**: PostgreSQL 15.x
- **Multi-AZ**: Yes (for production)
- **Storage**: GP3 SSD with 100GB minimum
- **Backup Retention**: 7 days minimum

### 2. Security Group Configuration

```bash
# Inbound Rules
Type: PostgreSQL
Protocol: TCP
Port: 5432
Source: Your application security group or VPC CIDR

# Outbound Rules
Type: All Traffic
Protocol: All
Port Range: All
Destination: 0.0.0.0/0
```

### 3. Parameter Group Settings

Create a custom parameter group with these optimizations:

```sql
-- Connection Settings
max_connections = 200
shared_preload_libraries = 'pg_stat_statements'

-- Memory Settings
shared_buffers = 25% of RAM
effective_cache_size = 75% of RAM
work_mem = 4MB
maintenance_work_mem = 64MB

-- Checkpoint Settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

-- Query Optimization
random_page_cost = 1.1
effective_io_concurrency = 200

-- Logging
log_statement = 'mod'
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
```

## Database Schema Optimizations

### Performance Indexes

The application includes comprehensive indexes optimized for common query patterns:

#### Composite Indexes
```sql
-- Shopping lists by kitchen and date
CREATE INDEX idx_shopping_lists_kitchen_created ON shopping_lists (kitchen_id, created_at);

-- Shopping list items by list and status
CREATE INDEX idx_shopping_list_items_list_purchased ON shopping_list_items (shopping_list_id, is_purchased);

-- Inventory items by kitchen and name
CREATE INDEX idx_pantry_items_kitchen_name ON pantry_items (kitchen_id, name);
CREATE INDEX idx_refrigerator_items_kitchen_name ON refrigerator_items (kitchen_id, name);
CREATE INDEX idx_freezer_items_kitchen_name ON freezer_items (kitchen_id, name);
```

#### Full-Text Search Indexes
```sql
-- GIN indexes for full-text search
CREATE INDEX idx_shopping_list_items_fulltext ON shopping_list_items 
USING gin(to_tsvector('english', coalesce(name, '') || ' ' || coalesce(description, '') || ' ' || coalesce(notes, '')));

CREATE INDEX idx_pantry_items_fulltext ON pantry_items 
USING gin(to_tsvector('english', coalesce(name, '') || ' ' || coalesce(description, '')));
```

#### Partial Indexes
```sql
-- Index only active users
CREATE INDEX idx_users_active_username ON users (username) WHERE is_active = true;
```

## Connection Pool Monitoring

### Health Check Endpoints

The application provides comprehensive database monitoring:

#### Basic Health Check
```bash
GET /api/v1/health
```

#### Detailed Database Status
```bash
GET /api/v1/database/status
```

#### Connection Pool Information
```bash
GET /api/v1/database/connections
```

#### Database Performance Metrics
```bash
GET /api/v1/database/performance
```

### Monitoring Metrics

The database manager tracks:
- **Connection Pool Status**: Active, idle, overflow connections
- **Response Times**: Connection and query performance
- **Error Rates**: Connection failures and timeouts
- **Resource Usage**: CPU, memory, and I/O metrics

## Performance Optimization

### Connection Pool Tuning

#### Pool Size Calculation
```python
# Formula: pool_size + max_overflow should not exceed RDS max_connections
# Recommended: 50-70% of max_connections for the application

# For db.t3.medium (max_connections = 200):
DB_POOL_SIZE = 20        # Base pool
DB_MAX_OVERFLOW = 30     # Additional connections
# Total possible: 50 connections (25% of max_connections)
```

#### Pool Timeout Settings
```python
# Balance between user experience and resource usage
DB_POOL_TIMEOUT = 30     # Wait 30 seconds for connection
DB_POOL_RECYCLE = 3600   # Recycle connections every hour
DB_POOL_PRE_PING = true  # Validate connections (prevents stale connections)
```

### Query Optimization

#### Prepared Statements
SQLAlchemy automatically uses prepared statements for better performance.

#### Connection Validation
```python
# Pre-ping validates connections before use
# Prevents "connection has been closed" errors
DB_POOL_PRE_PING = true
```

#### Statement Timeouts
```python
# Prevent long-running queries from blocking connections
DB_STATEMENT_TIMEOUT = 30000  # 30 seconds
DB_IDLE_TIMEOUT = 300000      # 5 minutes for idle transactions
```

## Security Configuration

### SSL/TLS Configuration

```python
# Force SSL connections in production
connect_args = {
    "sslmode": "require",
    "sslcert": "/path/to/client-cert.pem",      # Optional client cert
    "sslkey": "/path/to/client-key.pem",       # Optional client key
    "sslrootcert": "/path/to/ca-cert.pem"      # Optional CA cert
}
```

### Connection Security

```python
# Application name for connection tracking
DB_APPLICATION_NAME = "kitchen_manager_api"

# Connection timeout to prevent hanging connections
DB_CONNECT_TIMEOUT = 10
```

## Backup and Recovery

### Automated Backups

AWS RDS provides automated backups:
- **Backup Window**: Configure during low-traffic hours
- **Retention Period**: 7-30 days recommended
- **Point-in-Time Recovery**: Available within retention period

### Manual Snapshots

```bash
# Create manual snapshot
aws rds create-db-snapshot \
    --db-instance-identifier kitchen-manager-prod \
    --db-snapshot-identifier kitchen-manager-manual-$(date +%Y%m%d)
```

### Database Dumps

```bash
# Create logical backup
pg_dump -h your-rds-endpoint.region.rds.amazonaws.com \
        -U your_username \
        -d kitchen_manager \
        --no-password \
        --verbose \
        --format=custom \
        --file=kitchen_manager_backup_$(date +%Y%m%d).dump

# Restore from backup
pg_restore -h your-rds-endpoint.region.rds.amazonaws.com \
           -U your_username \
           -d kitchen_manager \
           --verbose \
           --clean \
           --if-exists \
           kitchen_manager_backup.dump
```

## Troubleshooting

### Common Issues

#### Connection Pool Exhaustion
```python
# Symptoms: "QueuePool limit of size X overflow Y reached"
# Solutions:
# 1. Increase pool_size or max_overflow
# 2. Reduce pool_timeout
# 3. Check for connection leaks in application code
# 4. Monitor long-running transactions
```

#### Connection Timeouts
```python
# Symptoms: "could not connect to server: Connection timed out"
# Solutions:
# 1. Check security group rules
# 2. Verify RDS instance status
# 3. Increase DB_CONNECT_TIMEOUT
# 4. Check network connectivity
```

#### SSL Connection Issues
```python
# Symptoms: "SSL connection has been closed unexpectedly"
# Solutions:
# 1. Verify SSL certificate validity
# 2. Check sslmode configuration
# 3. Update RDS certificate bundle
# 4. Verify client SSL configuration
```

### Monitoring Queries

#### Active Connections
```sql
SELECT 
    count(*) as total_connections,
    count(*) FILTER (WHERE state = 'active') as active,
    count(*) FILTER (WHERE state = 'idle') as idle,
    count(*) FILTER (WHERE application_name = 'kitchen_manager_api') as app_connections
FROM pg_stat_activity 
WHERE pid != pg_backend_pid();
```

#### Long-Running Queries
```sql
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query,
    state,
    application_name
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
AND state = 'active';
```

#### Connection Pool Status
```python
# Use the health endpoint
GET /api/v1/database/status

# Or check programmatically
from api.v1.database import db_manager
pool_status = db_manager.get_pool_status()
```

## Migration Strategy

### Zero-Downtime Migrations

1. **Create Migration**:
```bash
alembic revision -m "Description of changes"
```

2. **Test Migration**:
```bash
# Test on staging environment first
alembic upgrade head
```

3. **Production Deployment**:
```bash
# During maintenance window
alembic upgrade head
```

### Rollback Strategy

```bash
# Rollback to previous version
alembic downgrade -1

# Rollback to specific revision
alembic downgrade revision_id
```

## Performance Monitoring

### Key Metrics to Monitor

1. **Connection Pool Metrics**:
   - Pool utilization percentage
   - Connection wait times
   - Connection errors

2. **Query Performance**:
   - Average query response time
   - Slow query count
   - Query error rate

3. **Database Metrics**:
   - CPU utilization
   - Memory usage
   - I/O operations
   - Connection count

### Alerting Thresholds

```yaml
# Recommended CloudWatch alarms
DatabaseConnections: > 80% of max_connections
CPUUtilization: > 80%
FreeableMemory: < 512MB
ReadLatency: > 200ms
WriteLatency: > 200ms
```

## Best Practices

### Development
- Use connection pooling even in development
- Test with realistic data volumes
- Monitor query performance during development
- Use database migrations for schema changes

### Production
- Monitor connection pool utilization
- Set up automated backups
- Use read replicas for read-heavy workloads
- Implement proper error handling and retries
- Regular performance analysis and optimization

### Security
- Use SSL/TLS for all connections
- Implement proper authentication and authorization
- Regular security updates and patches
- Monitor for suspicious connection patterns
- Use VPC security groups for network isolation

This configuration provides a robust, scalable, and secure database setup optimized for AWS RDS PostgreSQL with comprehensive monitoring and performance optimization.