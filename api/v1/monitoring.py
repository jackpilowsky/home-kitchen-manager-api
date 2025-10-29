from fastapi import Request, Response
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
import psutil
import logging
from collections import defaultdict, deque
from threading import Lock
import asyncio
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)

@dataclass
class RequestMetrics:
    """Request metrics data structure"""
    timestamp: datetime
    method: str
    path: str
    status_code: int
    duration: float
    user_id: Optional[int] = None
    error_code: Optional[str] = None

@dataclass
class SystemMetrics:
    """System metrics data structure"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_percent: float
    active_connections: int
    request_count: int
    error_count: int
    avg_response_time: float

class MetricsCollector:
    """Centralized metrics collection and storage"""
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.request_metrics: deque = deque(maxlen=max_history)
        self.system_metrics: deque = deque(maxlen=1000)  # Keep last 1000 system snapshots
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.endpoint_stats: Dict[str, Dict] = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'error_count': 0,
            'last_accessed': None
        })
        self.user_activity: Dict[int, Dict] = defaultdict(lambda: {
            'request_count': 0,
            'last_activity': None,
            'error_count': 0
        })
        self._lock = Lock()
        self.start_time = datetime.utcnow()
    
    def record_request(self, metrics: RequestMetrics):
        """Record request metrics"""
        with self._lock:
            self.request_metrics.append(metrics)
            
            # Update endpoint statistics
            endpoint_key = f"{metrics.method} {metrics.path}"
            stats = self.endpoint_stats[endpoint_key]
            stats['count'] += 1
            stats['total_time'] += metrics.duration
            stats['last_accessed'] = metrics.timestamp
            
            if metrics.status_code >= 400:
                stats['error_count'] += 1
                if metrics.error_code:
                    self.error_counts[metrics.error_code] += 1
            
            # Update user activity
            if metrics.user_id:
                user_stats = self.user_activity[metrics.user_id]
                user_stats['request_count'] += 1
                user_stats['last_activity'] = metrics.timestamp
                if metrics.status_code >= 400:
                    user_stats['error_count'] += 1
    
    def record_system_metrics(self):
        """Record current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Count recent requests (last minute)
            now = datetime.utcnow()
            one_minute_ago = now - timedelta(minutes=1)
            
            recent_requests = [
                m for m in self.request_metrics 
                if m.timestamp >= one_minute_ago
            ]
            
            request_count = len(recent_requests)
            error_count = sum(1 for m in recent_requests if m.status_code >= 400)
            avg_response_time = (
                sum(m.duration for m in recent_requests) / request_count
                if request_count > 0 else 0.0
            )
            
            metrics = SystemMetrics(
                timestamp=now,
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_mb=memory.used / 1024 / 1024,
                disk_percent=disk.percent,
                active_connections=len(psutil.net_connections()),
                request_count=request_count,
                error_count=error_count,
                avg_response_time=avg_response_time
            )
            
            with self._lock:
                self.system_metrics.append(metrics)
                
            logger.debug(f"System metrics recorded: CPU {cpu_percent}%, Memory {memory.percent}%")
            
        except Exception as e:
            logger.error(f"Failed to record system metrics: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        try:
            now = datetime.utcnow()
            uptime = (now - self.start_time).total_seconds()
            
            # Get recent metrics
            recent_system = list(self.system_metrics)[-1] if self.system_metrics else None
            
            # Calculate error rates
            five_minutes_ago = now - timedelta(minutes=5)
            recent_requests = [
                m for m in self.request_metrics 
                if m.timestamp >= five_minutes_ago
            ]
            
            total_requests = len(recent_requests)
            error_requests = sum(1 for m in recent_requests if m.status_code >= 400)
            error_rate = error_requests / total_requests if total_requests > 0 else 0.0
            
            # Determine overall health
            health_status = "healthy"
            issues = []
            
            if recent_system:
                if recent_system.cpu_percent > 80:
                    health_status = "degraded"
                    issues.append("High CPU usage")
                if recent_system.memory_percent > 85:
                    health_status = "degraded"
                    issues.append("High memory usage")
                if error_rate > 0.1:  # 10% error rate
                    health_status = "unhealthy"
                    issues.append("High error rate")
            
            return {
                "status": health_status,
                "timestamp": now.isoformat(),
                "uptime_seconds": uptime,
                "issues": issues,
                "metrics": {
                    "requests_last_5min": total_requests,
                    "error_rate": error_rate,
                    "cpu_percent": recent_system.cpu_percent if recent_system else None,
                    "memory_percent": recent_system.memory_percent if recent_system else None,
                    "avg_response_time": recent_system.avg_response_time if recent_system else None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get health status: {e}")
            return {
                "status": "unknown",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get metrics summary for the specified time period"""
        try:
            now = datetime.utcnow()
            start_time = now - timedelta(hours=hours)
            
            # Filter metrics by time period
            period_requests = [
                m for m in self.request_metrics 
                if m.timestamp >= start_time
            ]
            
            if not period_requests:
                return {"message": "No data available for the specified period"}
            
            # Calculate statistics
            total_requests = len(period_requests)
            error_requests = sum(1 for m in period_requests if m.status_code >= 400)
            error_rate = error_requests / total_requests
            
            response_times = [m.duration for m in period_requests]
            avg_response_time = sum(response_times) / len(response_times)
            p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
            p99_response_time = sorted(response_times)[int(len(response_times) * 0.99)]
            
            # Top endpoints by request count
            endpoint_counts = defaultdict(int)
            for m in period_requests:
                endpoint_counts[f"{m.method} {m.path}"] += 1
            
            top_endpoints = sorted(
                endpoint_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
            
            # Error breakdown
            error_breakdown = defaultdict(int)
            for m in period_requests:
                if m.status_code >= 400 and m.error_code:
                    error_breakdown[m.error_code] += 1
            
            return {
                "period_hours": hours,
                "total_requests": total_requests,
                "error_rate": error_rate,
                "response_times": {
                    "avg": avg_response_time,
                    "p95": p95_response_time,
                    "p99": p99_response_time
                },
                "top_endpoints": top_endpoints,
                "error_breakdown": dict(error_breakdown),
                "timestamp": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {"error": str(e)}

# Global metrics collector instance
metrics_collector = MetricsCollector()

class MonitoringMiddleware:
    """Middleware for request monitoring and metrics collection"""
    
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger("api.monitoring")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        request_info = {
            "method": scope["method"],
            "path": scope["path"],
            "query_string": scope.get("query_string", b"").decode(),
            "client": scope.get("client"),
        }
        
        # Capture response
        response_info = {"status_code": 200}
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                response_info["status_code"] = message["status"]
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            response_info["status_code"] = 500
            self.logger.error(f"Request failed: {e}", exc_info=True)
            raise
        finally:
            # Record metrics
            end_time = time.time()
            duration = end_time - start_time
            
            metrics = RequestMetrics(
                timestamp=datetime.utcnow(),
                method=request_info["method"],
                path=request_info["path"],
                status_code=response_info["status_code"],
                duration=duration
            )
            
            metrics_collector.record_request(metrics)
            
            # Log request completion
            self.logger.info(
                f"{request_info['method']} {request_info['path']} - "
                f"{response_info['status_code']} - {duration:.3f}s",
                extra={
                    "method": request_info["method"],
                    "path": request_info["path"],
                    "status_code": response_info["status_code"],
                    "duration": duration,
                    "client_ip": request_info["client"][0] if request_info["client"] else None
                }
            )

class AlertManager:
    """Alert manager for monitoring thresholds and notifications"""
    
    def __init__(self):
        self.logger = logging.getLogger("api.alerts")
        self.alert_thresholds = {
            "error_rate": 0.05,  # 5%
            "response_time_p95": 2.0,  # 2 seconds
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0
        }
        self.alert_history: Dict[str, datetime] = {}
        self.alert_cooldown = timedelta(minutes=5)  # Minimum time between same alerts
    
    def check_alerts(self):
        """Check all alert conditions"""
        try:
            health_status = metrics_collector.get_health_status()
            
            # Check error rate
            error_rate = health_status["metrics"]["error_rate"]
            if error_rate > self.alert_thresholds["error_rate"]:
                self._trigger_alert(
                    "high_error_rate",
                    f"Error rate is {error_rate:.2%}, threshold is {self.alert_thresholds['error_rate']:.2%}",
                    "critical"
                )
            
            # Check response time
            avg_response_time = health_status["metrics"]["avg_response_time"]
            if avg_response_time and avg_response_time > self.alert_thresholds["response_time_p95"]:
                self._trigger_alert(
                    "slow_response_time",
                    f"Average response time is {avg_response_time:.3f}s, threshold is {self.alert_thresholds['response_time_p95']}s",
                    "warning"
                )
            
            # Check system resources
            cpu_percent = health_status["metrics"]["cpu_percent"]
            if cpu_percent and cpu_percent > self.alert_thresholds["cpu_percent"]:
                self._trigger_alert(
                    "high_cpu_usage",
                    f"CPU usage is {cpu_percent:.1f}%, threshold is {self.alert_thresholds['cpu_percent']}%",
                    "warning"
                )
            
            memory_percent = health_status["metrics"]["memory_percent"]
            if memory_percent and memory_percent > self.alert_thresholds["memory_percent"]:
                self._trigger_alert(
                    "high_memory_usage",
                    f"Memory usage is {memory_percent:.1f}%, threshold is {self.alert_thresholds['memory_percent']}%",
                    "critical"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to check alerts: {e}")
    
    def _trigger_alert(self, alert_type: str, message: str, severity: str):
        """Trigger an alert if not in cooldown period"""
        now = datetime.utcnow()
        last_alert = self.alert_history.get(alert_type)
        
        if last_alert and (now - last_alert) < self.alert_cooldown:
            return  # Still in cooldown period
        
        self.alert_history[alert_type] = now
        
        log_level = logging.CRITICAL if severity == "critical" else logging.WARNING
        self.logger.log(
            log_level,
            f"ALERT [{severity.upper()}] {alert_type}: {message}",
            extra={
                "alert_type": alert_type,
                "severity": severity,
                "message": message,
                "timestamp": now.isoformat()
            }
        )

# Global alert manager instance
alert_manager = AlertManager()

async def system_metrics_task():
    """Background task to collect system metrics and check alerts"""
    while True:
        try:
            metrics_collector.record_system_metrics()
            alert_manager.check_alerts()
            await asyncio.sleep(60)  # Run every minute
        except Exception as e:
            logger.error(f"System metrics task failed: {e}")
            await asyncio.sleep(60)

class PerformanceProfiler:
    """Performance profiler for detailed operation timing"""
    
    def __init__(self):
        self.logger = logging.getLogger("api.performance")
        self.operation_times: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()
    
    def record_operation(self, operation: str, duration: float):
        """Record operation timing"""
        with self._lock:
            self.operation_times[operation].append(duration)
            # Keep only last 1000 measurements per operation
            if len(self.operation_times[operation]) > 1000:
                self.operation_times[operation] = self.operation_times[operation][-1000:]
        
        # Log slow operations
        if duration > 1.0:  # Log operations taking more than 1 second
            self.logger.warning(
                f"Slow operation detected: {operation} took {duration:.3f}s",
                extra={
                    "operation": operation,
                    "duration": duration,
                    "threshold": 1.0
                }
            )
    
    def get_operation_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for a specific operation"""
        with self._lock:
            times = self.operation_times.get(operation, [])
            
            if not times:
                return {"count": 0}
            
            times_sorted = sorted(times)
            return {
                "count": len(times),
                "avg": sum(times) / len(times),
                "min": min(times),
                "max": max(times),
                "p50": times_sorted[len(times_sorted) // 2],
                "p95": times_sorted[int(len(times_sorted) * 0.95)],
                "p99": times_sorted[int(len(times_sorted) * 0.99)]
            }

# Global performance profiler instance
performance_profiler = PerformanceProfiler()

def profile_operation(operation_name: str):
    """Decorator to profile operation performance"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                performance_profiler.record_operation(operation_name, duration)
        
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                performance_profiler.record_operation(operation_name, duration)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator