from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

from .database import get_db
from .monitoring import metrics_collector, performance_profiler
from .exceptions import DatabaseException

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Comprehensive health check endpoint
    Returns overall system health status
    """
    try:
        health_status = metrics_collector.get_health_status()
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": "Health check failed"
        }

@router.get("/health/detailed", response_model=Dict[str, Any])
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check with component-specific status
    """
    health_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": "healthy",
        "components": {}
    }
    
    # Database health check
    try:
        db.execute(text("SELECT 1"))
        health_data["components"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_data["components"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        health_data["overall_status"] = "unhealthy"
    
    # System metrics health check
    try:
        system_health = metrics_collector.get_health_status()
        health_data["components"]["system_metrics"] = {
            "status": system_health["status"],
            "metrics": system_health["metrics"],
            "issues": system_health.get("issues", [])
        }
        
        if system_health["status"] != "healthy":
            health_data["overall_status"] = "degraded"
            
    except Exception as e:
        health_data["components"]["system_metrics"] = {
            "status": "unknown",
            "message": f"Failed to get system metrics: {str(e)}"
        }
    
    # Application health indicators
    try:
        # Check recent error rates
        now = datetime.utcnow()
        five_minutes_ago = now - timedelta(minutes=5)
        recent_requests = [
            m for m in metrics_collector.request_metrics 
            if m.timestamp >= five_minutes_ago
        ]
        
        if recent_requests:
            error_count = sum(1 for m in recent_requests if m.status_code >= 500)
            error_rate = error_count / len(recent_requests)
            
            health_data["components"]["application"] = {
                "status": "healthy" if error_rate < 0.05 else "degraded",
                "error_rate": error_rate,
                "total_requests": len(recent_requests),
                "error_count": error_count
            }
        else:
            health_data["components"]["application"] = {
                "status": "healthy",
                "message": "No recent requests to analyze"
            }
            
    except Exception as e:
        health_data["components"]["application"] = {
            "status": "unknown",
            "message": f"Failed to analyze application health: {str(e)}"
        }
    
    return health_data

@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Kubernetes-style readiness probe
    Returns 200 if service is ready to accept traffic
    """
    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))
        
        # Check if system is not overloaded
        health_status = metrics_collector.get_health_status()
        if health_status["status"] == "unhealthy":
            raise HTTPException(status_code=503, detail="System is unhealthy")
        
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/health/live")
async def liveness_check():
    """
    Kubernetes-style liveness probe
    Returns 200 if service is alive (basic functionality)
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": (datetime.utcnow() - metrics_collector.start_time).total_seconds()
    }

@router.get("/metrics", response_model=Dict[str, Any])
async def get_metrics(
    hours: int = Query(1, ge=1, le=24, description="Hours of metrics to retrieve")
):
    """
    Get application metrics for the specified time period
    """
    try:
        return metrics_collector.get_metrics_summary(hours=hours)
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@router.get("/metrics/system", response_model=Dict[str, Any])
async def get_system_metrics():
    """
    Get current system resource metrics
    """
    try:
        import psutil
        
        # Get current system stats
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        # Get recent system metrics from collector
        recent_metrics = list(metrics_collector.system_metrics)[-10:] if metrics_collector.system_metrics else []
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "current": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total_mb": memory.total / 1024 / 1024,
                    "used_mb": memory.used / 1024 / 1024,
                    "available_mb": memory.available / 1024 / 1024,
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": disk.total / 1024 / 1024 / 1024,
                    "used_gb": disk.used / 1024 / 1024 / 1024,
                    "free_gb": disk.free / 1024 / 1024 / 1024,
                    "percent": disk.percent
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            },
            "history": [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "cpu_percent": m.cpu_percent,
                    "memory_percent": m.memory_percent,
                    "memory_mb": m.memory_mb,
                    "request_count": m.request_count,
                    "error_count": m.error_count,
                    "avg_response_time": m.avg_response_time
                }
                for m in recent_metrics
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system metrics")

@router.get("/metrics/performance", response_model=Dict[str, Any])
async def get_performance_metrics():
    """
    Get performance metrics for different operations
    """
    try:
        operations = {}
        
        # Get stats for common operations
        common_operations = [
            "database_query",
            "authentication",
            "shopping_list_create",
            "shopping_list_update",
            "user_registration"
        ]
        
        for operation in common_operations:
            stats = performance_profiler.get_operation_stats(operation)
            if stats["count"] > 0:
                operations[operation] = stats
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "operations": operations
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve performance metrics")

@router.get("/metrics/endpoints", response_model=Dict[str, Any])
async def get_endpoint_metrics():
    """
    Get metrics for API endpoints
    """
    try:
        endpoint_stats = {}
        
        for endpoint, stats in metrics_collector.endpoint_stats.items():
            if stats['count'] > 0:
                endpoint_stats[endpoint] = {
                    "request_count": stats['count'],
                    "error_count": stats['error_count'],
                    "error_rate": stats['error_count'] / stats['count'],
                    "avg_response_time": stats['total_time'] / stats['count'],
                    "last_accessed": stats['last_accessed'].isoformat() if stats['last_accessed'] else None
                }
        
        # Sort by request count
        sorted_endpoints = dict(
            sorted(endpoint_stats.items(), key=lambda x: x[1]['request_count'], reverse=True)
        )
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": sorted_endpoints
        }
        
    except Exception as e:
        logger.error(f"Failed to get endpoint metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve endpoint metrics")

@router.get("/metrics/errors", response_model=Dict[str, Any])
async def get_error_metrics():
    """
    Get error metrics and breakdown
    """
    try:
        # Get recent error breakdown
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)
        
        recent_errors = [
            m for m in metrics_collector.request_metrics 
            if m.timestamp >= one_hour_ago and m.status_code >= 400
        ]
        
        # Group by status code
        status_code_breakdown = {}
        error_code_breakdown = {}
        
        for error in recent_errors:
            status_code = str(error.status_code)
            status_code_breakdown[status_code] = status_code_breakdown.get(status_code, 0) + 1
            
            if error.error_code:
                error_code_breakdown[error.error_code] = error_code_breakdown.get(error.error_code, 0) + 1
        
        return {
            "timestamp": now.isoformat(),
            "period_hours": 1,
            "total_errors": len(recent_errors),
            "status_code_breakdown": status_code_breakdown,
            "error_code_breakdown": error_code_breakdown,
            "recent_errors": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "method": e.method,
                    "path": e.path,
                    "status_code": e.status_code,
                    "error_code": e.error_code,
                    "duration": e.duration
                }
                for e in recent_errors[-20:]  # Last 20 errors
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get error metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve error metrics")

@router.get("/metrics/users", response_model=Dict[str, Any])
async def get_user_activity_metrics():
    """
    Get user activity metrics
    """
    try:
        # Get active users (users with activity in last 24 hours)
        now = datetime.utcnow()
        twenty_four_hours_ago = now - timedelta(hours=24)
        
        active_users = {}
        for user_id, stats in metrics_collector.user_activity.items():
            if stats['last_activity'] and stats['last_activity'] >= twenty_four_hours_ago:
                active_users[str(user_id)] = {
                    "request_count": stats['request_count'],
                    "error_count": stats['error_count'],
                    "last_activity": stats['last_activity'].isoformat()
                }
        
        return {
            "timestamp": now.isoformat(),
            "period_hours": 24,
            "active_user_count": len(active_users),
            "active_users": active_users
        }
        
    except Exception as e:
        logger.error(f"Failed to get user activity metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user activity metrics")