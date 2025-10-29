from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from collections import defaultdict

from .monitoring import metrics_collector, performance_profiler, alert_manager
from .validation import validate_bearer_token
from . import models

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/dashboard/overview", response_model=Dict[str, Any])
async def dashboard_overview(
    current_user: models.User = Depends(validate_bearer_token)
):
    """
    Get dashboard overview with key metrics
    Requires authentication for security
    """
    try:
        now = datetime.utcnow()
        
        # Get basic health status
        health_status = metrics_collector.get_health_status()
        
        # Get metrics for different time periods
        last_hour_metrics = metrics_collector.get_metrics_summary(hours=1)
        last_24h_metrics = metrics_collector.get_metrics_summary(hours=24)
        
        # Calculate trends
        hour_requests = last_hour_metrics.get("total_requests", 0)
        day_requests = last_24h_metrics.get("total_requests", 0)
        
        # Estimate requests per hour for the day
        avg_requests_per_hour = day_requests / 24 if day_requests > 0 else 0
        
        # Calculate trend (current hour vs average)
        request_trend = "stable"
        if avg_requests_per_hour > 0:
            trend_ratio = hour_requests / avg_requests_per_hour
            if trend_ratio > 1.2:
                request_trend = "increasing"
            elif trend_ratio < 0.8:
                request_trend = "decreasing"
        
        # Get top endpoints
        top_endpoints = last_24h_metrics.get("top_endpoints", [])[:5]
        
        # Get recent alerts (last 24 hours)
        recent_alerts = []
        twenty_four_hours_ago = now - timedelta(hours=24)
        
        # This would typically come from a persistent alert store
        # For now, we'll use the current alert status
        if health_status["status"] != "healthy":
            recent_alerts.append({
                "type": "system_health",
                "severity": "warning" if health_status["status"] == "degraded" else "critical",
                "message": f"System status: {health_status['status']}",
                "timestamp": now.isoformat(),
                "issues": health_status.get("issues", [])
            })
        
        return {
            "timestamp": now.isoformat(),
            "system_status": {
                "overall_health": health_status["status"],
                "uptime_seconds": health_status["uptime_seconds"],
                "issues": health_status.get("issues", [])
            },
            "request_metrics": {
                "last_hour": {
                    "total_requests": hour_requests,
                    "error_rate": last_hour_metrics.get("error_rate", 0),
                    "avg_response_time": last_hour_metrics.get("response_times", {}).get("avg", 0)
                },
                "last_24h": {
                    "total_requests": day_requests,
                    "error_rate": last_24h_metrics.get("error_rate", 0),
                    "avg_response_time": last_24h_metrics.get("response_times", {}).get("avg", 0)
                },
                "trend": request_trend
            },
            "system_resources": {
                "cpu_percent": health_status["metrics"].get("cpu_percent"),
                "memory_percent": health_status["metrics"].get("memory_percent"),
                "requests_last_5min": health_status["metrics"].get("requests_last_5min", 0)
            },
            "top_endpoints": top_endpoints,
            "recent_alerts": recent_alerts,
            "error_breakdown": last_24h_metrics.get("error_breakdown", {})
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard data")

@router.get("/dashboard/charts/requests", response_model=Dict[str, Any])
async def dashboard_request_charts(
    hours: int = Query(24, ge=1, le=168, description="Hours of data to retrieve"),
    interval_minutes: int = Query(60, ge=5, le=1440, description="Data point interval in minutes"),
    current_user: models.User = Depends(validate_bearer_token)
):
    """
    Get request metrics data for charts
    """
    try:
        now = datetime.utcnow()
        start_time = now - timedelta(hours=hours)
        interval = timedelta(minutes=interval_minutes)
        
        # Create time buckets
        time_buckets = []
        current_time = start_time
        while current_time <= now:
            time_buckets.append(current_time)
            current_time += interval
        
        # Initialize data structures
        request_counts = []
        error_counts = []
        response_times = []
        
        # Process metrics by time bucket
        for i, bucket_start in enumerate(time_buckets[:-1]):
            bucket_end = time_buckets[i + 1]
            
            # Filter requests in this time bucket
            bucket_requests = [
                m for m in metrics_collector.request_metrics
                if bucket_start <= m.timestamp < bucket_end
            ]
            
            # Calculate metrics for this bucket
            total_requests = len(bucket_requests)
            error_requests = sum(1 for m in bucket_requests if m.status_code >= 400)
            
            if bucket_requests:
                avg_response_time = sum(m.duration for m in bucket_requests) / len(bucket_requests)
            else:
                avg_response_time = 0
            
            request_counts.append({
                "timestamp": bucket_start.isoformat(),
                "value": total_requests
            })
            
            error_counts.append({
                "timestamp": bucket_start.isoformat(),
                "value": error_requests
            })
            
            response_times.append({
                "timestamp": bucket_start.isoformat(),
                "value": avg_response_time
            })
        
        return {
            "period_hours": hours,
            "interval_minutes": interval_minutes,
            "data": {
                "request_counts": request_counts,
                "error_counts": error_counts,
                "response_times": response_times
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get request chart data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chart data")

@router.get("/dashboard/charts/system", response_model=Dict[str, Any])
async def dashboard_system_charts(
    hours: int = Query(24, ge=1, le=168, description="Hours of data to retrieve"),
    current_user: models.User = Depends(validate_bearer_token)
):
    """
    Get system metrics data for charts
    """
    try:
        now = datetime.utcnow()
        start_time = now - timedelta(hours=hours)
        
        # Filter system metrics by time period
        system_data = [
            m for m in metrics_collector.system_metrics
            if m.timestamp >= start_time
        ]
        
        # Format data for charts
        cpu_data = []
        memory_data = []
        request_rate_data = []
        
        for metric in system_data:
            timestamp = metric.timestamp.isoformat()
            
            cpu_data.append({
                "timestamp": timestamp,
                "value": metric.cpu_percent
            })
            
            memory_data.append({
                "timestamp": timestamp,
                "value": metric.memory_percent
            })
            
            request_rate_data.append({
                "timestamp": timestamp,
                "value": metric.request_count  # Requests per minute
            })
        
        return {
            "period_hours": hours,
            "data": {
                "cpu_usage": cpu_data,
                "memory_usage": memory_data,
                "request_rate": request_rate_data
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get system chart data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system chart data")

@router.get("/dashboard/alerts", response_model=Dict[str, Any])
async def dashboard_alerts(
    hours: int = Query(24, ge=1, le=168, description="Hours of alert history"),
    current_user: models.User = Depends(validate_bearer_token)
):
    """
    Get alert history and current alert status
    """
    try:
        now = datetime.utcnow()
        
        # Get current system status
        health_status = metrics_collector.get_health_status()
        
        # Get alert thresholds
        thresholds = alert_manager.alert_thresholds
        
        # Get recent alert history (this would typically come from persistent storage)
        alert_history = []
        
        # Check current conditions against thresholds
        current_alerts = []
        
        # Check error rate
        error_rate = health_status["metrics"]["error_rate"]
        if error_rate > thresholds["error_rate"]:
            current_alerts.append({
                "type": "high_error_rate",
                "severity": "critical",
                "message": f"Error rate {error_rate:.2%} exceeds threshold {thresholds['error_rate']:.2%}",
                "current_value": error_rate,
                "threshold": thresholds["error_rate"],
                "timestamp": now.isoformat()
            })
        
        # Check response time
        avg_response_time = health_status["metrics"]["avg_response_time"]
        if avg_response_time and avg_response_time > thresholds["response_time_p95"]:
            current_alerts.append({
                "type": "slow_response_time",
                "severity": "warning",
                "message": f"Response time {avg_response_time:.3f}s exceeds threshold {thresholds['response_time_p95']}s",
                "current_value": avg_response_time,
                "threshold": thresholds["response_time_p95"],
                "timestamp": now.isoformat()
            })
        
        # Check system resources
        cpu_percent = health_status["metrics"]["cpu_percent"]
        if cpu_percent and cpu_percent > thresholds["cpu_percent"]:
            current_alerts.append({
                "type": "high_cpu_usage",
                "severity": "warning",
                "message": f"CPU usage {cpu_percent:.1f}% exceeds threshold {thresholds['cpu_percent']}%",
                "current_value": cpu_percent,
                "threshold": thresholds["cpu_percent"],
                "timestamp": now.isoformat()
            })
        
        memory_percent = health_status["metrics"]["memory_percent"]
        if memory_percent and memory_percent > thresholds["memory_percent"]:
            current_alerts.append({
                "type": "high_memory_usage",
                "severity": "critical",
                "message": f"Memory usage {memory_percent:.1f}% exceeds threshold {thresholds['memory_percent']}%",
                "current_value": memory_percent,
                "threshold": thresholds["memory_percent"],
                "timestamp": now.isoformat()
            })
        
        return {
            "timestamp": now.isoformat(),
            "current_alerts": current_alerts,
            "alert_history": alert_history,
            "thresholds": thresholds,
            "alert_summary": {
                "total_active": len(current_alerts),
                "critical_count": sum(1 for a in current_alerts if a["severity"] == "critical"),
                "warning_count": sum(1 for a in current_alerts if a["severity"] == "warning")
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get alert data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alert data")

@router.get("/dashboard/performance", response_model=Dict[str, Any])
async def dashboard_performance(
    current_user: models.User = Depends(validate_bearer_token)
):
    """
    Get performance analysis data
    """
    try:
        # Get performance stats for key operations
        operations = [
            "database_query",
            "authentication", 
            "shopping_list_create",
            "shopping_list_update",
            "user_registration"
        ]
        
        performance_data = {}
        for operation in operations:
            stats = performance_profiler.get_operation_stats(operation)
            if stats["count"] > 0:
                performance_data[operation] = stats
        
        # Get slowest endpoints
        slow_endpoints = []
        for endpoint, stats in metrics_collector.endpoint_stats.items():
            if stats['count'] > 0:
                avg_time = stats['total_time'] / stats['count']
                if avg_time > 0.5:  # Endpoints taking more than 500ms on average
                    slow_endpoints.append({
                        "endpoint": endpoint,
                        "avg_response_time": avg_time,
                        "request_count": stats['count'],
                        "error_rate": stats['error_count'] / stats['count']
                    })
        
        # Sort by response time
        slow_endpoints.sort(key=lambda x: x['avg_response_time'], reverse=True)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "operation_performance": performance_data,
            "slow_endpoints": slow_endpoints[:10],  # Top 10 slowest
            "performance_summary": {
                "total_operations_tracked": len(performance_data),
                "slowest_operation": max(
                    performance_data.items(), 
                    key=lambda x: x[1]["avg"], 
                    default=(None, {"avg": 0})
                )[0] if performance_data else None
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve performance data")

@router.post("/dashboard/alerts/acknowledge", response_model=Dict[str, Any])
async def acknowledge_alert(
    alert_type: str,
    current_user: models.User = Depends(validate_bearer_token)
):
    """
    Acknowledge an alert (mark as seen)
    """
    try:
        # In a real implementation, this would update persistent storage
        # For now, we'll just log the acknowledgment
        
        logger.info(
            f"Alert acknowledged by user {current_user.id}",
            extra={
                "alert_type": alert_type,
                "user_id": current_user.id,
                "username": current_user.username,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return {
            "status": "acknowledged",
            "alert_type": alert_type,
            "acknowledged_by": current_user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to acknowledge alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to acknowledge alert")