# Monitoring and Observability Documentation

## Overview
The Home Kitchen Manager API includes comprehensive monitoring and observability features for production deployment, performance analysis, and system health tracking.

## Architecture

### Components
- **MetricsCollector**: Centralized metrics collection and storage
- **MonitoringMiddleware**: Request/response monitoring and timing
- **AlertManager**: Threshold-based alerting system
- **PerformanceProfiler**: Operation-level performance tracking
- **Health Checks**: Kubernetes-compatible health endpoints
- **Dashboard APIs**: Real-time monitoring dashboard data

### Data Flow
```
Request → MonitoringMiddleware → MetricsCollector → AlertManager
                ↓                        ↓              ↓
        PerformanceProfiler → Dashboard APIs → Health Checks
```

## Metrics Collection

### Request Metrics
Automatically collected for every API request:
- **Timestamp**: When the request occurred
- **Method & Path**: HTTP method and endpoint
- **Status Code**: Response status
- **Duration**: Request processing time
- **User ID**: Authenticated user (if applicable)
- **Error Code**: Specific error code (if error occurred)

### System Metrics
Collected every minute:
- **CPU Usage**: Current CPU utilization percentage
- **Memory Usage**: RAM utilization and available memory
- **Disk Usage**: Disk space utilization
- **Network Stats**: Bytes sent/received, packet counts
- **Active Connections**: Current database/network connections
- **Request Rate**: Requests per minute
- **Error Rate**: Errors per minute

### Performance Metrics
Operation-level timing for:
- Database queries
- Authentication operations
- Business logic operations
- External API calls
- File operations

## Health Checks

### Basic Health Check
**Endpoint**: `GET /api/v1/health`
**Purpose**: Overall system health status
**Response**:
```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "uptime_seconds": 86400,
  "issues": ["High CPU usage"],
  "metrics": {
    "requests_last_5min": 150,
    "error_rate": 0.02,
    "cpu_percent": 45.2,
    "memory_percent": 67.8,
    "avg_response_time": 0.234
  }
}
```

### Detailed Health Check
**Endpoint**: `GET /api/v1/health/detailed`
**Purpose**: Component-specific health status
**Components Checked**:
- Database connectivity
- System resource usage
- Application error rates
- External service dependencies

### Kubernetes Probes

#### Readiness Probe
**Endpoint**: `GET /api/v1/health/ready`
**Purpose**: Determine if service can accept traffic
**Checks**:
- Database connectivity
- System not overloaded
- Critical dependencies available

#### Liveness Probe
**Endpoint**: `GET /api/v1/health/live`
**Purpose**: Determine if service is alive
**Response**: Simple alive status with uptime

## Metrics Endpoints

### Application Metrics
**Endpoint**: `GET /api/v1/metrics?hours=24`
**Data Provided**:
- Total requests and error rates
- Response time percentiles (P95, P99)
- Top endpoints by traffic
- Error breakdown by type
- Request trends and patterns

### System Metrics
**Endpoint**: `GET /api/v1/metrics/system`
**Data Provided**:
- Current system resource usage
- Historical system metrics
- Resource utilization trends
- Network and disk statistics

### Performance Metrics
**Endpoint**: `GET /api/v1/metrics/performance`
**Data Provided**:
- Operation timing statistics
- Slowest operations identification
- Performance trend analysis
- Bottleneck detection

### Endpoint Metrics
**Endpoint**: `GET /api/v1/metrics/endpoints`
**Data Provided**:
- Request count per endpoint
- Error rate per endpoint
- Average response time per endpoint
- Most/least used endpoints

### Error Metrics
**Endpoint**: `GET /api/v1/metrics/errors`
**Data Provided**:
- Error count and breakdown
- Error trends over time
- Most common error types
- Recent error details

## Dashboard APIs

### Overview Dashboard
**Endpoint**: `GET /api/v1/dashboard/overview`
**Authentication**: Required
**Data Provided**:
- System health summary
- Key performance indicators
- Recent alerts and issues
- Traffic and error trends

### Chart Data APIs

#### Request Charts
**Endpoint**: `GET /api/v1/dashboard/charts/requests`
**Parameters**:
- `hours`: Time period (1-168 hours)
- `interval_minutes`: Data point interval (5-1440 minutes)
**Data**: Time-series data for requests, errors, response times

#### System Charts
**Endpoint**: `GET /api/v1/dashboard/charts/system`
**Data**: Time-series data for CPU, memory, request rates

### Alert Management
**Endpoint**: `GET /api/v1/dashboard/alerts`
**Features**:
- Current active alerts
- Alert history and trends
- Configurable thresholds
- Alert acknowledgment

## Alerting System

### Alert Types
- **High Error Rate**: Error rate exceeds 5%
- **Slow Response Time**: P95 response time > 2 seconds
- **High CPU Usage**: CPU usage > 80%
- **High Memory Usage**: Memory usage > 85%
- **High Disk Usage**: Disk usage > 90%

### Alert Thresholds
```python
{
    "error_rate": 0.05,        # 5%
    "response_time_p95": 2.0,  # 2 seconds
    "cpu_percent": 80.0,       # 80%
    "memory_percent": 85.0,    # 85%
    "disk_percent": 90.0       # 90%
}
```

### Alert Cooldown
- **Minimum interval**: 5 minutes between same alert types
- **Prevents spam**: Avoids repeated alerts for same condition
- **Escalation**: Alerts can escalate if conditions worsen

## Performance Profiling

### Operation Profiling
Use the `@profile_operation` decorator:
```python
from api.v1.monitoring import profile_operation

@profile_operation("user_registration")
def register_user(user_data):
    # Function implementation
    pass
```

### Automatic Profiling
Automatically profiles:
- Database operations
- Authentication flows
- API endpoint handlers
- External service calls

### Performance Analysis
- **Average timing**: Mean operation duration
- **Percentiles**: P50, P95, P99 response times
- **Trend analysis**: Performance over time
- **Bottleneck identification**: Slowest operations

## Logging Integration

### Structured Logging
All monitoring events use structured logging:
```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "level": "INFO",
  "logger": "api.monitoring",
  "message": "Request completed",
  "method": "GET",
  "path": "/api/v1/shopping-lists/",
  "status_code": 200,
  "duration": 0.234,
  "user_id": 123
}
```

### Log Categories
- **api.monitoring**: Request/response monitoring
- **api.alerts**: Alert notifications and acknowledgments
- **api.performance**: Performance analysis and slow operations
- **api.security**: Security-related monitoring events

## Configuration

### Environment Variables
```bash
# Monitoring Configuration
MONITORING_ENABLED=true
METRICS_RETENTION_HOURS=168  # 7 days
ALERT_COOLDOWN_MINUTES=5
PERFORMANCE_THRESHOLD_SECONDS=1.0

# Alert Thresholds
ALERT_ERROR_RATE_THRESHOLD=0.05
ALERT_RESPONSE_TIME_THRESHOLD=2.0
ALERT_CPU_THRESHOLD=80.0
ALERT_MEMORY_THRESHOLD=85.0
```

### Monitoring Middleware Configuration
```python
# Enable/disable monitoring
app.add_middleware(MonitoringMiddleware)

# Configure metrics collector
metrics_collector = MetricsCollector(max_history=10000)

# Configure alert manager
alert_manager = AlertManager()
alert_manager.alert_thresholds["error_rate"] = 0.03  # 3%
```

## Production Deployment

### Docker Configuration
```dockerfile
# Install system monitoring dependencies
RUN apt-get update && apt-get install -y \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health/live || exit 1
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kitchen-manager-api
spec:
  template:
    spec:
      containers:
      - name: api
        image: kitchen-manager-api:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /api/v1/health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Prometheus Integration
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'kitchen-manager-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/api/v1/metrics'
    scrape_interval: 30s
```

## Grafana Dashboard

### Key Panels
1. **System Overview**
   - Request rate and error rate
   - Response time percentiles
   - System resource usage

2. **Performance Analysis**
   - Endpoint performance breakdown
   - Slow operation identification
   - Database query performance

3. **Error Analysis**
   - Error rate trends
   - Error type breakdown
   - Recent error details

4. **System Resources**
   - CPU and memory usage
   - Disk and network utilization
   - Active connections

### Sample Queries
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"4..|5.."}[5m]) / rate(http_requests_total[5m])

# Response time P95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Memory usage
process_resident_memory_bytes / 1024 / 1024
```

## Alerting Rules

### Prometheus Alerting Rules
```yaml
groups:
- name: kitchen-manager-api
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
```

## Troubleshooting

### Common Issues

#### High Memory Usage
1. Check metrics: `GET /api/v1/metrics/system`
2. Analyze request patterns: `GET /api/v1/metrics/endpoints`
3. Review slow operations: `GET /api/v1/metrics/performance`
4. Check for memory leaks in application code

#### High Error Rate
1. Check error breakdown: `GET /api/v1/metrics/errors`
2. Review recent errors and patterns
3. Check database connectivity
4. Analyze authentication failures

#### Slow Response Times
1. Check performance metrics: `GET /api/v1/metrics/performance`
2. Identify slow endpoints: `GET /api/v1/dashboard/performance`
3. Analyze database query performance
4. Check system resource usage

### Monitoring Best Practices

1. **Set Appropriate Thresholds**
   - Based on historical data and SLA requirements
   - Avoid alert fatigue with too-sensitive thresholds
   - Regular review and adjustment

2. **Monitor Key Metrics**
   - Request rate and error rate
   - Response time percentiles
   - System resource usage
   - Database performance

3. **Use Structured Logging**
   - Consistent log format across all components
   - Include correlation IDs for request tracking
   - Log at appropriate levels

4. **Regular Health Checks**
   - Automated health monitoring
   - Dependency health verification
   - Proactive issue detection

5. **Performance Baselines**
   - Establish performance baselines
   - Monitor for performance degradation
   - Capacity planning based on trends

## Security Considerations

### Access Control
- Dashboard endpoints require authentication
- Sensitive metrics protected from unauthorized access
- Role-based access for different monitoring levels

### Data Privacy
- No sensitive data in metrics or logs
- User IDs anonymized in public metrics
- Compliance with data protection regulations

### Monitoring Security
- Monitor for suspicious activity patterns
- Track authentication failures and patterns
- Alert on unusual traffic or error patterns