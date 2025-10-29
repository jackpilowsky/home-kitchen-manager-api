from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.engine import Engine
from contextlib import contextmanager
import logging
import time
from typing import Generator
import psycopg2

from config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Enhanced database manager with connection pooling and monitoring"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._setup_engine()
        self._setup_event_listeners()
    
    def _setup_engine(self):
        """Setup SQLAlchemy engine with optimized settings for AWS RDS PostgreSQL"""
        
        # Connection arguments optimized for AWS RDS
        connect_args = {
            "connect_timeout": settings.database.connect_timeout,
            "sslmode": settings.database.ssl_mode,
            "application_name": settings.database.application_name,
            "options": f"-c statement_timeout={settings.database.statement_timeout}ms "
                      f"-c idle_in_transaction_session_timeout={settings.database.idle_in_transaction_session_timeout}ms"
        }
        
        # Choose pool class based on environment
        if settings.app.environment == 'production':
            poolclass = QueuePool
        else:
            # Use NullPool for development to avoid connection issues
            poolclass = NullPool if settings.app.debug else QueuePool
        
        # Engine configuration
        engine_kwargs = {
            "poolclass": poolclass,
            "echo": settings.app.debug and settings.app.log_level == 'DEBUG',
            "echo_pool": settings.app.debug,
            "future": True,  # Use SQLAlchemy 2.0 style
            "connect_args": connect_args,
        }
        
        # Add pool settings only for QueuePool
        if poolclass == QueuePool:
            engine_kwargs.update({
                "pool_size": settings.database.pool_size,
                "max_overflow": settings.database.max_overflow,
                "pool_timeout": settings.database.pool_timeout,
                "pool_recycle": settings.database.pool_recycle,
                "pool_pre_ping": settings.database.pool_pre_ping,
            })
        
        try:
            self.engine = create_engine(
                settings.database.database_url,
                **engine_kwargs
            )
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
                logger.info("Database connection established successfully")
            
            # Setup session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
                expire_on_commit=False
            )
            
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            raise
    
    def _setup_event_listeners(self):
        """Setup SQLAlchemy event listeners for monitoring and optimization"""
        
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set PostgreSQL-specific connection parameters"""
            if hasattr(dbapi_connection, 'cursor'):
                cursor = dbapi_connection.cursor()
                # Set connection-level parameters for better performance
                cursor.execute("SET timezone = 'UTC'")
                cursor.execute("SET statement_timeout = %s", (settings.database.statement_timeout,))
                cursor.execute("SET idle_in_transaction_session_timeout = %s", 
                             (settings.database.idle_in_transaction_session_timeout,))
                cursor.close()
        
        @event.listens_for(Engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log connection checkout for monitoring"""
            logger.debug("Connection checked out from pool")
        
        @event.listens_for(Engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Log connection checkin for monitoring"""
            logger.debug("Connection returned to pool")
        
        @event.listens_for(Engine, "invalidate")
        def receive_invalidate(dbapi_connection, connection_record, exception):
            """Log connection invalidation"""
            logger.warning(f"Connection invalidated: {exception}")
    
    def get_session(self):
        """Get database session with proper error handling"""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()
    
    def health_check(self) -> dict:
        """Perform database health check"""
        try:
            start_time = time.time()
            
            with self.engine.connect() as conn:
                # Test basic connectivity
                result = conn.execute("SELECT 1 as health_check")
                result.fetchone()
                
                # Get connection pool status
                pool_status = {
                    "pool_size": self.engine.pool.size() if hasattr(self.engine.pool, 'size') else 'N/A',
                    "checked_in": self.engine.pool.checkedin() if hasattr(self.engine.pool, 'checkedin') else 'N/A',
                    "checked_out": self.engine.pool.checkedout() if hasattr(self.engine.pool, 'checkedout') else 'N/A',
                    "overflow": self.engine.pool.overflow() if hasattr(self.engine.pool, 'overflow') else 'N/A',
                }
                
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                return {
                    "status": "healthy",
                    "response_time_ms": round(response_time, 2),
                    "pool_status": pool_status,
                    "database_url": settings.database.database_url.split('@')[1] if '@' in settings.database.database_url else 'hidden'
                }
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": None,
                "pool_status": None
            }
    
    def get_pool_status(self) -> dict:
        """Get detailed connection pool status"""
        if not hasattr(self.engine.pool, 'size'):
            return {"status": "Pool monitoring not available"}
        
        return {
            "pool_size": self.engine.pool.size(),
            "checked_in_connections": self.engine.pool.checkedin(),
            "checked_out_connections": self.engine.pool.checkedout(),
            "overflow_connections": self.engine.pool.overflow(),
            "total_connections": self.engine.pool.size() + self.engine.pool.overflow(),
        }
    
    def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")

# Global database manager instance
db_manager = DatabaseManager()

# Backward compatibility
engine = db_manager.engine
SessionLocal = db_manager.SessionLocal

def get_db() -> Generator:
    """
    Dependency function to get database session
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = db_manager.get_session()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def get_db_context():
    """
    Context manager for database sessions
    
    Usage:
        with get_db_context() as db:
            # Use db session
            pass
    """
    db = db_manager.get_session()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database transaction error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Database utility functions
def execute_raw_sql(sql: str, params: dict = None) -> list:
    """Execute raw SQL query safely"""
    with get_db_context() as db:
        result = db.execute(sql, params or {})
        return result.fetchall()

def get_database_info() -> dict:
    """Get database server information"""
    try:
        with get_db_context() as db:
            result = db.execute("""
                SELECT 
                    version() as version,
                    current_database() as database_name,
                    current_user as current_user,
                    inet_server_addr() as server_address,
                    inet_server_port() as server_port
            """)
            row = result.fetchone()
            
            return {
                "version": row[0] if row else None,
                "database_name": row[1] if row else None,
                "current_user": row[2] if row else None,
                "server_address": row[3] if row else None,
                "server_port": row[4] if row else None,
            }
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {"error": str(e)}