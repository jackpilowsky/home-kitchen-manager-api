import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import time

from api.v1.monitoring import (
    MetricsCollector, 
    RequestMetrics, 
    SystemMetrics,
    PerformanceProfiler,
    profile_operation
)

def test_metrics_collector_request_recording():
    """Test request metrics recording"""
    collector = MetricsCollector()
    
    # Record some test metrics
    metrics1 = RequestMetrics(
        timestamp=datetime.utcnow(),
        method="GET",
        path="/api/v1/shopping-lists/",
        status_code=200,
        duration=0.5,
        user_id=1
    )
    
    metrics2 = RequestMetrics(
        timestamp=datetime.utcnow(),
        method="POST",
        path="/api/v1/shopping-lists/",
        status_code=400,
        duration=0.3,
        error_code="VALIDATION_ERROR"
    )
    
    collector.record_request(metrics1)
    collector.record_request(metrics2)
    
    # Check that metrics were recorded
    assert len(collector.request_metrics) == 2
    assert collector.endpoint_stats["GET /api/v1/shopping-lists/"]["count"] == 1
    assert collector.endpoint_stats["POST /api/v1/shopping-lists/"]["count"] == 1
    assert collector.endpoint_stats["POST /api/v1/shopping-lists/"]["error_count"] == 1
    assert collector.error_counts["VALIDATION_ERROR"] == 1

def test_metrics_collector_health_status():
    """Test health status generation"""
    collector = MetricsCollector()
    
    # Add some test data
    now = datetime.utcnow()
    
    # Add recent requests with some errors
    for i in range(10):
        status_code = 500 if i < 2 else 200  # 20% error rate
        metrics = RequestMetrics(
            timestamp=now - timedelta(minutes=1),
            method="GET",
            path="/test",
            status_code=status_code,
            duration=0.1
        )
        collector.record_request(metrics)
    
    health_status = collector.get_health_status()
    
    assert "status" in health_status
    assert "metrics" in health_status
    assert "timestamp" in health_status
    assert health_status["metrics"]["requests_last_5min"] == 10

def test_metrics_collector_summary():
    """Test metrics summary generation"""
    collector = MetricsCollector()
    
    # Add test data
    now = datetime.utcnow()
    
    for i in range(5):
        metrics = RequestMetrics(
            timestamp=now - timedelta(minutes=30),  # Within 1 hour
            method="GET",
            path="/test",
            status_code=200,
            duration=0.1 + (i * 0.05)  # Varying response times
        )
        collector.record_request(metrics)
    
    summary = collector.get_metrics_summary(hours=1)
    
    assert summary["total_requests"] == 5
    assert summary["error_rate"] == 0.0
    assert "response_times" in summary
    assert "top_endpoints" in summary

def test_performance_profiler():
    """Test performance profiler functionality"""
    profiler = PerformanceProfiler()
    
    # Record some operation times
    profiler.record_operation("test_operation", 0.5)
    profiler.record_operation("test_operation", 0.3)
    profiler.record_operation("test_operation", 0.7)
    
    stats = profiler.get_operation_stats("test_operation")
    
    assert stats["count"] == 3
    assert stats["avg"] == pytest.approx(0.5, rel=1e-2)
    assert stats["min"] == 0.3
    assert stats["max"] == 0.7

def test_profile_operation_decorator():
    """Test the profile_operation decorator"""
    profiler = PerformanceProfiler()
    
    @profile_operation("decorated_function")
    def test_function():
        time.sleep(0.1)
        return "result"
    
    # Monkey patch the global profiler for testing
    import api.v1.monitoring
    original_profiler = api.v1.monitoring.performance_profiler
    api.v1.monitoring.performance_profiler = profiler
    
    try:
        result = test_function()
        assert result == "result"
        
        stats = profiler.get_operation_stats("decorated_function")
        assert stats["count"] == 1
        assert stats["avg"] >= 0.1  # Should be at least 100ms
    finally:
        # Restore original profiler
        api.v1.monitoring.performance_profiler = original_profiler

def test_health_endpoint(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "uptime_seconds" in data

def test_health_detailed_endpoint(client: TestClient):
    """Test detailed health check endpoint"""
    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    
    data = response.json()
    assert "overall_status" in data
    assert "components" in data
    assert "database" in data["components"]
    assert "system_metrics" in data["components"]

def test_health_ready_endpoint(client: TestClient):
    """Test readiness probe endpoint"""
    response = client.get("/api/v1/health/ready")
    # Should be 200 if ready, 503 if not ready
    assert response.status_code in [200, 503]

def test_health_live_endpoint(client: TestClient):
    """Test liveness probe endpoint"""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "alive"
    assert "uptime" in data

def test_metrics_endpoint(client: TestClient):
    """Test metrics endpoint"""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    
    data = response.json()
    # Should have basic structure even with no data
    assert isinstance(data, dict)

def test_metrics_with_parameters(client: TestClient):
    """Test metrics endpoint with parameters"""
    response = client.get("/api/v1/metrics?hours=2")
    assert response.status_code == 200
    
    # Test invalid parameters
    response = client.get("/api/v1/metrics?hours=25")  # Too many hours
    assert response.status_code == 422

def test_system_metrics_endpoint(client: TestClient):
    """Test system metrics endpoint"""
    response = client.get("/api/v1/metrics/system")
    assert response.status_code == 200
    
    data = response.json()
    assert "current" in data
    assert "history" in data
    assert "cpu_percent" in data["current"]
    assert "memory" in data["current"]

def test_performance_metrics_endpoint(client: TestClient):
    """Test performance metrics endpoint"""
    response = client.get("/api/v1/metrics/performance")
    assert response.status_code == 200
    
    data = response.json()
    assert "operations" in data
    assert "timestamp" in data

def test_endpoint_metrics_endpoint(client: TestClient):
    """Test endpoint metrics endpoint"""
    response = client.get("/api/v1/metrics/endpoints")
    assert response.status_code == 200
    
    data = response.json()
    assert "endpoints" in data
    assert "timestamp" in data

def test_error_metrics_endpoint(client: TestClient):
    """Test error metrics endpoint"""
    response = client.get("/api/v1/metrics/errors")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_errors" in data
    assert "status_code_breakdown" in data
    assert "error_code_breakdown" in data

def test_dashboard_overview_requires_auth(client: TestClient):
    """Test that dashboard endpoints require authentication"""
    response = client.get("/api/v1/dashboard/overview")
    assert response.status_code == 401

def test_dashboard_overview_with_auth(client: TestClient, auth_headers):
    """Test dashboard overview with authentication"""
    response = client.get("/api/v1/dashboard/overview", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "system_status" in data
    assert "request_metrics" in data
    assert "system_resources" in data

def test_dashboard_charts_requests(client: TestClient, auth_headers):
    """Test dashboard request charts endpoint"""
    response = client.get("/api/v1/dashboard/charts/requests", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "data" in data
    assert "request_counts" in data["data"]
    assert "error_counts" in data["data"]
    assert "response_times" in data["data"]

def test_dashboard_charts_system(client: TestClient, auth_headers):
    """Test dashboard system charts endpoint"""
    response = client.get("/api/v1/dashboard/charts/system", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "data" in data

def test_dashboard_alerts(client: TestClient, auth_headers):
    """Test dashboard alerts endpoint"""
    response = client.get("/api/v1/dashboard/alerts", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "current_alerts" in data
    assert "thresholds" in data
    assert "alert_summary" in data

def test_dashboard_performance(client: TestClient, auth_headers):
    """Test dashboard performance endpoint"""
    response = client.get("/api/v1/dashboard/performance", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "operation_performance" in data
    assert "slow_endpoints" in data

def test_acknowledge_alert(client: TestClient, auth_headers):
    """Test alert acknowledgment endpoint"""
    response = client.post(
        "/api/v1/dashboard/alerts/acknowledge?alert_type=test_alert",
        headers=auth_headers
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "acknowledged"
    assert data["alert_type"] == "test_alert"

def test_monitoring_middleware_integration(client: TestClient):
    """Test that monitoring middleware is working"""
    # Make a request to generate metrics
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    # Check that metrics were recorded
    from api.v1.monitoring import metrics_collector
    assert len(metrics_collector.request_metrics) > 0
    
    # Find our request in the metrics
    health_requests = [
        m for m in metrics_collector.request_metrics
        if m.path == "/api/v1/health" and m.method == "GET"
    ]
    assert len(health_requests) > 0

def test_metrics_collector_thread_safety():
    """Test that metrics collector is thread-safe"""
    import threading
    
    collector = MetricsCollector()
    
    def add_metrics():
        for i in range(100):
            metrics = RequestMetrics(
                timestamp=datetime.utcnow(),
                method="GET",
                path=f"/test/{i}",
                status_code=200,
                duration=0.1
            )
            collector.record_request(metrics)
    
    # Start multiple threads
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=add_metrics)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Should have 500 total requests (5 threads * 100 requests each)
    assert len(collector.request_metrics) == 500