import logging
import logging.config
from datetime import datetime
import os

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(funcName)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(pathname)s %(lineno)d %(funcName)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": "logs/error.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        }
    },
    "loggers": {
        "": {  # Root logger
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "api.v1": {
            "level": "DEBUG",
            "handlers": ["console", "file", "error_file"],
            "propagate": False
        },
        "auth": {
            "level": "DEBUG",
            "handlers": ["console", "file", "error_file"],
            "propagate": False
        },
        "sqlalchemy.engine": {
            "level": "WARNING",
            "handlers": ["file"],
            "propagate": False
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False
        },
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["console", "error_file"],
            "propagate": False
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["file"],
            "propagate": False
        }
    }
}

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Apply logging configuration
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Logging configuration initialized")

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)

# Request logging middleware
class RequestLoggingMiddleware:
    def __init__(self, app):
        self.app = app
        self.logger = get_logger("api.middleware.request")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = datetime.utcnow()
            
            # Log request start
            self.logger.info(
                f"Request started: {scope['method']} {scope['path']}",
                extra={
                    "method": scope["method"],
                    "path": scope["path"],
                    "query_string": scope.get("query_string", b"").decode(),
                    "client": scope.get("client"),
                    "start_time": start_time.isoformat()
                }
            )
            
            # Process request
            await self.app(scope, receive, send)
            
            # Log request completion
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.info(
                f"Request completed: {scope['method']} {scope['path']} - Duration: {duration:.3f}s",
                extra={
                    "method": scope["method"],
                    "path": scope["path"],
                    "duration": duration,
                    "end_time": end_time.isoformat()
                }
            )
        else:
            await self.app(scope, receive, send)

# Security logging
class SecurityLogger:
    def __init__(self):
        self.logger = get_logger("api.security")
    
    def log_authentication_attempt(self, username: str, success: bool, ip_address: str = None):
        """Log authentication attempts"""
        level = logging.INFO if success else logging.WARNING
        message = f"Authentication {'successful' if success else 'failed'} for user: {username}"
        
        self.logger.log(
            level,
            message,
            extra={
                "event_type": "authentication",
                "username": username,
                "success": success,
                "ip_address": ip_address
            }
        )
    
    def log_authorization_failure(self, user_id: int, resource: str, action: str, ip_address: str = None):
        """Log authorization failures"""
        self.logger.warning(
            f"Authorization denied: User {user_id} attempted {action} on {resource}",
            extra={
                "event_type": "authorization_failure",
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "ip_address": ip_address
            }
        )
    
    def log_suspicious_activity(self, description: str, user_id: int = None, ip_address: str = None):
        """Log suspicious activities"""
        self.logger.error(
            f"Suspicious activity detected: {description}",
            extra={
                "event_type": "suspicious_activity",
                "description": description,
                "user_id": user_id,
                "ip_address": ip_address
            }
        )

# Performance logging
class PerformanceLogger:
    def __init__(self):
        self.logger = get_logger("api.performance")
    
    def log_slow_query(self, query: str, duration: float, threshold: float = 1.0):
        """Log slow database queries"""
        if duration > threshold:
            self.logger.warning(
                f"Slow query detected: {duration:.3f}s",
                extra={
                    "event_type": "slow_query",
                    "query": query,
                    "duration": duration,
                    "threshold": threshold
                }
            )
    
    def log_high_memory_usage(self, memory_mb: float, threshold: float = 500.0):
        """Log high memory usage"""
        if memory_mb > threshold:
            self.logger.warning(
                f"High memory usage: {memory_mb:.1f}MB",
                extra={
                    "event_type": "high_memory",
                    "memory_mb": memory_mb,
                    "threshold": threshold
                }
            )

# Initialize loggers
security_logger = SecurityLogger()
performance_logger = PerformanceLogger()